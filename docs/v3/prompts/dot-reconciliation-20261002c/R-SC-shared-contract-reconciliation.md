---
title: R-SC — Shared contract reconciliation
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-SC — Shared contract reconciliation

This is a reconciliation handoff for accepted Owner decisions D-018, D-019, D-022, D-024 and
D-031. It consumes the overnight integration synthesis and the mutually delegated lane reports
listed under [Inputs to read](#inputs-to-read), and it produces **one accepted-candidate shared
field map** plus the conflict table and decisive vectors that would falsify it. It selects no
language, store, framework, runtime, transport, encoding, schema or vendor.

## Baked context

### Shared Recursion context

Recursion is a standalone agent harness **and** a harness orchestrator that delegates through
other harnesses. The development target is Recursion v3: a small deterministic kernel with typed
adapters; native and upstream execution; persistent, goal-scoped assistants organized as
Head -> ARM executives -> bounded workers (no separate AI "ARM manager"); configurable context and
compaction; plugins and editions; an interactive detachable terminal (CLI, optional Telegram); and
Windows/Linux operation and recovery.

Authority: Lucas is the final owner. Hermes-led control was retired on 2026-09-28
(state/DECISIONS.md D-017); **Hermes is an optional upstream integration, not the executive control
plane.** Workers are bounded executors. An implementer's own PASS is never acceptance; independent
review is required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes, spending,
deployment, publication or merge.

Accepted Owner decisions this handoff bakes in and may not reopen:

- **D-018** — Recursion is both a first-class native harness and a unifying wrapper over the wider
  harness ecosystem, to remove lock-in and cut quota/usage burn, under a community open-source
  posture; vendor-intent quota claims remain a falsifiable hypothesis, not fact.
- **D-019** — build comprehensively, ship lean, install opt-in: every accepted capability is built
  and ships as an opt-in plugin/profile, never active by default.
- **D-022** — one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes **Aggressive / Full / Lazy**, plus `checkpoint`, `interrupt` and `drain`. A
  source interrupt, socket close or killed PID is not external rollback.
- **D-024** — productive continuity is the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting.
- **D-031** — no vendor-sabotage claim: savings are claimed only when measured per workload.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula, captures
and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs, pinned
source, licenses, peer-reviewed work). Classify every consequential claim as source-documented,
locally observed, inferred or unverified; keep `unknown` distinct from zero. Model consensus and
vendor marketing are not evidence. Every recommendation needs a competing option and a decisive
falsifier, and must name what it does not prove. Do not request or display hidden
chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never secrets,
credentials, personal data, private repository content, local paths, or account/infrastructure
identifiers.

### Lane context

- The reconciliation target is the **shared contract spine** the overnight lanes delegated to each
  other, not a lane's private internals. The whole point is that identity domains, content
  envelopes, commands and receipts, publication ordering and resource conservation must mean the
  same thing on every lane, or the integration silently double-counts, re-issues an effect or
  widens a disclosure.
- The synthesis already fixed the house style: identity is a typed reference vector in a declared
  domain, never one magic generation; a projection never promotes itself to an authoritative
  observation; a local admission record, Stop request or launch receipt alone cannot supply
  receiver-side authority. Do not relitigate those.
- The synthesis named the cross-lane defects it wants resolved rather than restated: the initial
  X `TransferBinding` published before copy/evidence/accounting registration; Q `CopyRecord` has no
  planned/staged enum, so a separate disclosure-intent relation is proposed; the L/V command
  identity mismatch; and the requirement that Q `coverage_and_loss` plus T `loss_manifest` resolve
  to one loss record. This handoff proposes the accepted candidates and the vectors that decide
  them.
- D-022's vocabulary is fixed and must appear as distinct facts, not flattened into one status:
  request accepted, local fence installed, remote fence observed, interrupt delivered, process
  exited, containment empty, effects settled and independently verified are separate. `checkpoint`,
  `interrupt` and `drain` remain mechanisms, not modes.
- D-024 requires that continuity never be purchased by duplicating live authority: a fork, a
  harness change, a compaction or a machine move may carry forward evidence and accounting lineage
  but must never clone an active grant, approval, lease, writer token, launch permit or
  reservation. A reservation split, if allowed, is its own conserving canonical operation.
- D-031 forbids inferring vendor intent from quota/limit/spend observations; a resource conflict
  is resolved by evidence, not by a narrative.
- Prior work this handoff depends on and must not restate: the lane reports
  [R-L](../../research-lane/overnight-20261002/rl/report.md) (interface platform),
  [R-P](../../research-lane/overnight-20261002/rp/report.md) (untrusted input),
  [R-Q](../../research-lane/overnight-20261002/rq/report.md) (durable memory),
  [R-T](../../research-lane/overnight-20261002/rt/report.md) (multimodal I/O),
  [R-V](../../research-lane/overnight-20261002/rv/report.md) (observability/replay),
  [R-X](../../research-lane/overnight-20261002/rx/report.md) (node fabric) and
  [R-Y](../../research-lane/overnight-20261002/ry/report.md) (workspace graph), plus the synthesis
  [ownership and field map](../../research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md),
  [model architecture](../../research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md) and
  [integration test handoff](../../research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md).
- Evidence status: no shared contract has been implemented, ratified as wire, or validated by an
  independent runtime oracle. The Q base/T/X/Y candidate declarations were found textually
  compatible at the pinned intake; that is a static integration result, not an implemented
  guarantee. Every reconciliation below is a candidate pending independent vectors and Owner
  adoption.

## Purpose

Produce the decision-ready **shared contract reconciliation candidate** for Recursion: one accepted
candidate for each shared field, identity and ordering rule that the mutually delegated lanes
currently describe differently; a per-field owner and source lane for that candidate; a conflict
table with the decisive vectors that distinguish the competing readings; and an explicit statement
of what the reconciliation does not prove. The candidate resolves the L/V canonical command key,
the Artifact/ContentEnvelope base with its one loss record, the receipt-stage vocabulary that must
not flatten to one boolean, the remote-disclosure/task-publication ordering, the resource
conservation invariants, and the open joins recorded by the synthesis. It ends with a versioned
epoch map proposal, a receipt-retention/replay boundary, a digest-domain binding rule, the route
freeze set, the coherent-capture/apply rule and the fence-install-barrier rule. It does not select
a language, store, framework, schema, transport, encoding or vendor, does not qualify a route, and
executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, transport, encoding, schema format,
contract-definition language or vendor.** Do not decide an Owner question recorded in D-018,
D-019, D-022, D-024 or D-031. Treat the lane candidate contracts as prior proposals cited from the
named reports, not as ratified wire or endorsed components. No provider, model, account, node,
receiver or live system is contacted; no schema is deployed; no credential is touched. Do not
claim that field-name agreement, a passing JSON schema or a shared library proves semantics,
privacy or authority. Do not collapse a fact vector into a single success boolean, invent a global
total order or clock, infer a remote copy is present from an intent, or let a projection promote
itself to an authoritative observation. Frozen M1A/M1B/M1C bytes and meanings are preserved, not
reinterpreted.

## Inputs to read

Read these repository files; they are the exact inputs and the reconciliation must cite them
rather than paraphrase them loosely:

- Synthesis: [OWNERSHIP-AND-FIELD-MAP.md](../../research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md),
  [MODEL-ARCHITECTURE.md](../../research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md),
  [INTEGRATION-TEST-HANDOFF.md](../../research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md).
- Lane reports: [R-L](../../research-lane/overnight-20261002/rl/report.md),
  [R-Q](../../research-lane/overnight-20261002/rq/report.md),
  [R-P](../../research-lane/overnight-20261002/rp/report.md),
  [R-T](../../research-lane/overnight-20261002/rt/report.md),
  [R-V](../../research-lane/overnight-20261002/rv/report.md),
  [R-X](../../research-lane/overnight-20261002/rx/report.md),
  [R-Y](../../research-lane/overnight-20261002/ry/report.md).
- Machine-readable candidate contracts where a field name is disputed: R-L `proposed-contracts.json`,
  R-Q `candidate-contracts.json`, R-T `artifact-contract.json` and `field-map.json` (revision 2),
  R-V `candidate-contracts.json`, R-X `candidate-contracts.json`, R-Y `candidate-contracts.json`,
  R-P `proposed-contracts.json`.

No private source, connector, credential or live system is read. Where a field is used below with
an exact spelling, that spelling is taken from the named candidate contract and must be preserved
exactly; inventing a new synonym is a reconciliation failure.

## Research questions

### Identity domains that must never collapse

1. Produce the accepted-candidate reference vector for each of these independent domains, naming
   the domain, the exact candidate field name(s), the issuer/owner and the one relation that binds
   it to the current object. They must **not** be compared or ordered across domains:
   `writer_fence` / `writer_epoch`; `work_epoch` / work lease / `work_fence`; `pause_epoch` /
   `pause_fence`; the role/coordination lease versus work execution versus terminal input/resize
   control; `process_incarnation` versus `node_incarnation`; `route_epoch` versus
   `route_descriptor_epoch`; `context_epoch`; `configuration_revision` versus
   `configuration_epoch`; `release_identity` versus `release_epoch`;
   `command_id` versus `logical_operation_id` versus `attempt_id`; and
   `workspace_id` / `repository_id` / `instance_id` / `snapshot_ref` / `materialization_id`.
   Which single generic `epoch` field, if any, is admissible, and what must it name to avoid the
   "new process heals an old work fence" error?
2. For each identity, give the decisive vector that proves collapse is wrong. Examples to settle:
   a PID reuse matching a copied session; a process incarnation advanced while the work epoch is
   still revoked; a route descriptor updated without a new route assignment; a configuration
   content revision bump without a new effective/application generation; a release activation
   epoch advanced while old work authority stays revoked. State the exact refusal each vector must
   produce.
3. Reconcile the **evidence positions** so they remain distinct cuts with causal joins, never one
   invented total order or global clock: canonical ordinal, receipt-journal cut, observation
   sequence, stream cursor (`event` versus `utf8-byte`), byte offset, and projection generation.
   Which pairs may be joined, under what declared relation, and which joins must return `unknown`
   rather than a guessed order?

### The canonical command key

4. Resolve the audited L/V mismatch. R-L originally deduplicated in authority-domain / principal /
   command-ID scope; R-V uses an authority-domain plus immutable command ID/digest with the
   actor/auth reference bound in the bytes. Propose the accepted candidate for the canonical
   command key and justify it against the competing option. The synthesis proposes
   `(admitted_authority_domain, command_id)`; state whether that is the accepted candidate, what
   `content_digest` checks under it, and why `actor_id`/`auth_ref` belong inside the immutable
   command rather than in a second namespace.
5. Specify the decisive vectors that distinguish the candidates: (a) same canonical ID, same
   bytes, same principal; (b) same canonical ID, same bytes, changed principal/auth reference;
   (c) same canonical ID, changed body/payload; (d) two client principal-local subnamespaces whose
   local IDs collide, with and without a declared injective durable mapping; (e) an expired
   deduplication history that must yield `receipt-history-unavailable` rather than permission to
   resend. For each, state the accepted outcome and the falsifier.
6. Separate command delivery identity, logical effect identity and dispatch-attempt identity, and
   state which one the retry owner keys on across a crash, a reconnect, a provider-session
   replacement and a new node incarnation. State how a still-readable historical receipt after
   effect revocation stays history and never re-dispatches.

### The Artifact / ContentEnvelope contract

7. Fix the shared content base. Adopt the single internal `ArtifactRef` as exactly
   `(object_type, id, version, content_digest)`, with the digest a byte-integrity identity inside
   the declared privacy domain, and an outward `opaque_handle` as a separately authorized,
   audience/purpose-scoped locator that is not a serialized `ArtifactRef` and not a grant. State
   why possession-based authority must be classified separately, and where R-T, R-Y and R-X may
   extend but not fork the base.
8. Fix the `ContentEnvelope` required field names exactly as the candidate contract gives them,
   including `project_and_audience`, `privacy_domain_id` and `authority_carried_none`. Confirm
   `project_id` belongs to the memory projection and is **not** a base-envelope alias. Give the
   decisive vector for an omitted `project_and_audience`, a substituted `project_id`, an omitted
   `privacy_domain_id`, and an unknown security-relevant mandatory field.
9. Collapse the two loss views into **one** loss record or one record with typed facets. Reconcile
   Q `coverage_and_loss` with T `loss_manifest` so there are not two writable loss truths, while
   preserving T's distinct media/loss dimensions and the rule that unknown semantic preservation
   stays unknown. State the alias/conflict rule that rejects contradictory loss declarations.
10. Reconcile the receipt-stage vocabulary so it never flattens to one boolean or one success
    enum, and every stage names its subject and observer. At minimum keep these distinct:
    `received`, `delivered`, `admitted`, `started`, `observed`, `settled`, `verified`, plus the
    local-only `saved_locally` stage. Map each to its source-lane evidence requirement and its
    explicit non-proof (for example: transport received is not durable admission; delivered is not
    model consumption or adoption; applied-observed is not independent verification; settled is not
    task acceptance).

### Publication ordering

11. Reconcile remote disclosure and task publication into one ordering that is the same for every
    transferring lane. The candidate sequence is: private local staging within an admitted resource
    envelope -> durable registration of exact disclosure intent, expected potential-copy inventory
    linkage, known lineage and applicable reservation -> current rights/fence check -> release of
    the admitted manifest metadata/chunk -> verify actual received representation and register its
    copy/lineage -> current rights/fence check -> task publication -> append publication/disclosure
    observations and reconcile settlement.
12. Give the decisive vectors for the initial X `TransferBinding` defect and its correction: crash
    before and after each step; revoke after staging and before publication; lose the
    acknowledgement after publication; race a deletion-inventory fence. State why remote quarantine
    is already disclosure to that node, why an intent does not prove a present copy or transmission,
    why a possible disclosure after crash stays `unknown`, and why Q `CopyRecord` must not silently
    gain a planned/staged status.

### Resource invariants

13. Reconcile the resource contract to one conserving algebra and state the representation choice
    explicitly: gross cumulative cap with disjoint headroom
    (`settled + outstanding + withheld + proposed <= gross limit`) versus an ordinary-work net cap
    that subtracts withheld exactly once. Enumerate and justify the shared invariants: settled
    consumption and outstanding reservations are disjoint; uncertain liabilities **annotate** the
    outstanding reservation and are never added a second time; a recovery/control reserve is
    disjoint or tagged exactly once under a documented rule; a strict cap requires a trustworthy
    finite upper bound; settlement transfers the reserved liability to measured consumption
    atomically and releases only proven-unused remainder; retry, fork, new session, route switch,
    machine loss and calendar rollover cannot recredit a task.
14. Give the decisive vectors: an unknown bound that must refuse strict-cap expansion rather than
    become infinite; an uncertain liability counted twice; a protected recovery reserve counted
    twice or subtracted and re-added; a parent-inclusive meter that must not be added to its child
    totals; a raw crash-time `0` that stays `unknown` rather than known zero; a duplicate
    settlement. State how each is counted exactly once.

### Open joins to resolve

15. Propose a **versioned semantic map** for the differently named writer/work/pause/configuration
    epochs, so differently named candidate fields map to a typed envelope without mutating frozen
    contracts. Say what the map must carry (domain, issuer, relation, version) and what it must
    refuse (cross-domain ordering, silent renaming of a frozen field).
16. Freeze **receipt retention and logical-command replay** as a boundary: how retained receipts
    support authorized historical disclosure and duplicate-delivery evidence while a repeated
    delivery journal occurrence is distinct from unique logical-command replay input, and what
    happens when retention expires (reconcile/hold, never treat missing history as permission to
    resend).
17. Define **digest-domain binding** at the containing schema: because the four-field
    `ArtifactRef` alone does not carry every interpretation parameter, state which algorithm/domain,
    normalization, coverage and schema fields bind a digest and what a conflicting duplicate under
    the same key does.
18. Specify the **route freeze** set: the exact per-route inputs, Stop semantics, child ownership,
    compaction, metering and required capability/trust support that must be frozen before work is
    admitted; and the rule that a descriptor update does not create a route assignment while a new
    assignment cannot cure stale capability evidence.
19. Specify **coherent capture and protected apply** on an exact workspace/platform profile,
    including the ABA vector that equal endpoint hashes miss, aliases and missing external objects,
    the three capture classes (immutable closure, enforced quiescence, bounded validated capture)
    and which one must refuse a coherent-fork requirement.
20. Specify the **receiver fence install barrier** and pre-install exposure classification: why
    canonical revocation is not proof of remote installation, why an already-dispatched external
    effect during the exposure interval stays unresolved, and why a conflicting replacement effect
    must wait for install evidence or independent quiescence.
21. State the **independent runtime evidence** still required. What is merely static agreement
    between candidate schemas, and what would an independent oracle have to observe before any
    field map, conservation equation or ordering claim moves from candidate to accepted?

## Deliverable

A shared-contract reconciliation candidate containing:

- An **accepted-candidate field map**: one row per shared field/identity/ordering rule, with the
  exact candidate name, the single proposed design owner, the source lane, the consuming lanes and
  the binding relation. It must cover the identity domains in Q1, the canonical command key in
  Q4-Q6, the `ArtifactRef`/`ContentEnvelope`/loss/receipt fields in Q7-Q10, the publication
  ordering in Q11-Q12, and the resource invariants in Q13-Q14.
- A **conflict table** with decisive vectors: for every field where lanes disagreed or could be
  read two ways, the competing readings, the accepted candidate (or an explicit `unresolved`
  disposition), the exact falsifying vector that distinguishes them, and what passing does not
  prove.
- An **epoch/identity envelope proposal** (Q15) that is versioned and additive to frozen
  contracts, plus the receipt-retention/replay, digest-domain, route-freeze,
  coherent-capture/apply and fence-barrier join resolutions (Q16-Q21).
- **Explicit non-proofs**: what the reconciliation does not establish, including that schema/name
  agreement is not implemented semantics, that no independent runtime oracle has run, that no
  route is qualified, that no privacy/erasure/containment guarantee follows from field parity, and
  that no measured performance or economic benefit is claimed.

Every recommendation names a competing option, a decisive falsifier and what it does not prove. No
language, store, framework, runtime, transport, encoding, schema format, contract-definition
language or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, database, framework, runtime, sandbox,
  transport, encoding, schema format, contract-definition language, index, model or vendor.
- No amendment or reinterpretation of frozen M1A, M1B or M1C payloads, and no new M1B wire arm;
  `GAP` and Stop keep their frozen meanings, and application envelopes stay a separate versioned
  layer.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no new Owner question decided.
- No route qualification, account/subscription entitlement claim or eligibility finding.
- No claim that a field map, a passing schema, or name agreement constitutes implemented semantics,
  authorization, privacy or durability.
- No provider, model, credential, account, node or receiver call; every vector is synthetic and
  provider-free.
- No fabrication of independent runtime evidence; static compatibility is not a runtime oracle.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The identity-domain section gives an accepted-candidate reference vector for every domain in Q1,
  states the one generic `epoch` disposition, and supplies the decisive collapse vector for each
  with the refusal it must produce.
- The canonical command key is resolved to one accepted candidate with the `content_digest`,
  `actor_id`/`auth_ref` and principal-local-mapping rules stated, and all five Q5 vectors with
  their expected outcome and falsifier, while historical receipts after revocation stay history.
- The shared content base adopts the exact four-field `ArtifactRef`, the exact required
  `ContentEnvelope` names including `project_and_audience`, `privacy_domain_id` and
  `authority_carried_none`, rejects a `project_id` base alias, collapses `coverage_and_loss` plus
  `loss_manifest` to one loss record, and keeps the receipt stages distinct with each stage's
  non-proof named.
- The publication ordering is stated once for all transferring lanes and includes the pre-release
  disclosure-intent/copy-inventory/lineage/reservation registration, the two rights/fence checks,
  the verify/register step, publish and reconcile, with Q12 vectors and the CopyRecord no-planned-
  status rule.
- The resource contract states gross-cap versus net-cap explicitly, asserts disjoint settled vs
  outstanding, annotation-not-addition for uncertain liabilities, the finite-bound requirement for
  a strict cap and atomic settlement, with the Q14 vectors counted exactly once.
- The open joins are answered: a versioned epoch map, a receipt-retention/replay boundary, a
  digest-domain binding rule, a route-freeze set, a coherent-capture/apply rule and a fence-install
  barrier, each with a competing option, a decisive falsifier and a non-proof.
- The deliverable contains the field map with per-field owner and source lane, the conflict table
  with decisive vectors, and the explicit non-proofs; every recommendation has a competing option,
  a decisive falsifier and what it does not prove; no language, store, framework, runtime,
  transport, encoding, schema format, contract-definition language or vendor is selected and no
  route is qualified.
- Protected paths are untouched; privacy and secret scan are clean.
