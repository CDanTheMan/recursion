---
title: Recursion v3 architecture-proof and planning-baseline result
status: correction-candidate-after-independent-adjudication
last-updated: 2026-09-03
source-checkpoint: 672081fc1874ab9b7a41a14ca61adc60ecd71c95
source-baseline: 98113d6c6d3debe2a4d207c51bb1780f7356d714
---

# Recursion v3 architecture-proof and planning-baseline result

This is the durable synthesis of the 2026-09-03 evidence-closure and autonomous-planning
campaign. It is a documentation result. It does not prove that a v3 runtime exists, authorize
implementation, ratify Option 2, change the constitution, configure a provider, permit spending,
or authorize publication, deployment, service changes, or a private canary.

The exact campaign inputs, immutable demonstration `GoalSpec`, plan revisions, task DAG,
worker packets, gates, and disposition are in
[AUTONOMOUS-PLANNING-CAMPAIGN.md](AUTONOMOUS-PLANNING-CAMPAIGN.md). The canonical proposed
planning semantics are in [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). The independently
reconstructed evidence for every R1-R17 lane is in
[R1-R17-EVIDENCE.md](R1-R17-EVIDENCE.md).

## Orientation and preflight

- The requested branch was `codex/v3-design-foundation` at the exact requested starting HEAD
  `672081fc1874ab9b7a41a14ca61adc60ecd71c95`, and the worktree was clean.
- `6543840cfd4dd1d7f49ce58b55e8357cdf3b37be` was and remains an ancestor. No newer work was
  discarded.
- The target worktree had no `AGENTS.md`. The effective session-supplied repository instructions,
  then complete `CONTROL_PLANE.md`, `ANCHOR.md`, active `docs/v3/**`, requested commits, and
  `612eb2b04acd92e34f1fe5702ceba5474221c6bc..HEAD` diff were read before planning or delegation.
- Writes were restricted to `docs/v3/**`. No Codex, provider, authentication, plugin,
  environment, route, account, or spending setting was modified.
- The eight Luna lanes ran in two waves of four. The inter-wave resource and account-limit
  observations supported the second wave; they were admission observations, not benchmarks or
  entitlement claims.

## Research and review envelope

| Packet | Exact route | Assignment | Outcome |
|---|---|---|---|
| `WP-V3DF-101` | `gpt-5.6-luna`, `xhigh` | Reconstruct R1-R4 | Conditional Option 2 support; current immediate PAUSE and process-containment limits retained. |
| `WP-V3DF-102` | `gpt-5.6-luna`, `xhigh` | Reconstruct R5-R8 | Same-family limitation, SQLite primitive/authority separation, and preregistered admission control retained. |
| `WP-V3DF-103` | `gpt-5.6-luna`, `xhigh` | Reconstruct R9-R12 | Deletion, canary, terminal/process, and performance claims narrowed to testable contracts. |
| `WP-V3DF-104` | `gpt-5.6-luna`, `xhigh` | Reconstruct R13-R17 | Route, cache, canonicalization, scholarly, and whole-v3 claims retained as hypotheses or contracts, not results. |
| `WP-V3DF-201` | `gpt-5.6-luna`, `xhigh` | Plan lifecycle | Amendment, fencing, stale-work, replay, and authority semantics proposed. |
| `WP-V3DF-202` | `gpt-5.6-luna`, `xhigh` | DAG and retry semantics | Deterministic readiness, conflict, retry, replan, and cancellation rules proposed. |
| `WP-V3DF-203` | `gpt-5.6-luna`, `xhigh` | Primary-source audit | Source versions, licenses, contradictory SQLite evidence, and expiry triggers corrected. |
| `WP-V3DF-204` | `gpt-5.6-luna`, `xhigh` | Lean adversarial review | The broad first milestone was rejected and narrowed to M1A. |
| `WP-V3DF-301` | `gpt-5.6-terra`, `xhigh` | Authority adjudication | Conditional support; added complete prompt traceability, exact downgrade binding, and a sixth constitutional conflict. |
| `WP-V3DF-302` | `gpt-5.6-terra`, `xhigh` | Final evidence/readiness adjudication | Returned `adapt` on `16e16cf`; its `bd98c41` recheck confirmed hygiene/provenance/oracle-count repairs but returned `reject/adapt` for three missing source records, underdetermined compatibility/novelty subgrammars and a verifier-downgrade enum conflict. PR-V3DF-20260903-05 supplies the next exact correction candidate. |

Sol, Luna, and Terra are GPT-5.6-family routes. Terra is an independent worker role here, not an
external-family verifier. No current external-family packet was sent. An already configured,
explicitly approved, non-metered external-family route with known model/reasoning mapping could
not be established within the allowed read-only route boundary. The prior session's claimed Muse
input and output were not preserved and could not be recovered; they are labelled historical
unrecovered assertions and carry no evidentiary weight. Grok was not used. No provider was added,
enabled, guessed, substituted, or billed.

## Evidence closure

All R1-R17 lanes now have persistent records containing the exact question, claims, primary
sources and revisions, contradictory evidence, applicability and limitations, confidence,
adoption decision, decisive falsifier, and worker/adjudicator disposition. Evidence classes are
explicit: directly reverified evidence, repository-local inference, owner decision,
prior-session assertion not independently recovered, and unverified hypothesis.

The claim registry now describes the rows that actually exist. Fabricated empty ranges were
removed; `TAA-*`, `TPE-*`, `APC-*`, and `XFR-*` are registered. A machine-readable registry plus
a deterministic validator rejects duplicate or malformed IDs, missing registered rows,
unregistered claim rows, unreserved gaps, and references to nonexistent IDs. Claim rows were not
invented to fill declared ranges.

Consequential external sources were personally opened by the Sol lead. Version-sensitive facts
are revision-pinned where practical and otherwise carry an explicit revalidation trigger. In
particular:

- SQLite's official [isolation documentation](https://www.sqlite.org/isolation.html) establishes
  serialized writes; [WAL](https://www.sqlite.org/wal.html) describes a concurrency mechanism.
  Neither defines Recursion authority, lease fencing, PAUSE, or effect admission. The 2026 WAL
  reset-corruption correction is retained as contradictory version-sensitive evidence.
- TUF is pinned to specification 1.0.36/source revision, SLSA to v1.2/source revision, and W3C
  PROV to dated Recommendations. They establish update/provenance structures, not safety or
  truth.
- Terminal and containment sources are pinned to Windows ConPTY/Job Object documentation, Linux
  cgroup v2 documentation, POSIX.1-2024 Issue 8, and SSH RFC 4254. Each has explicit portability
  and containment limits.
- OpenAI, Anthropic, and Gemini caching controls are recorded separately. Provider caches are not
  assumed uniformly controllable or portable. API cache documents do not establish Codex OAuth
  CLI behavior, subscription debit, or cross-provider reuse.
- Scholarly identifiers and metadata are separated from claim truth, applicability, correction,
  retraction, access, and license state.

## Autonomous-planning baseline

The proposed deterministic flow is:

```text
OwnerIntent -> draft GoalSpec -> Owner-accepted GoalSpec
             -> Head starts ArmRun -> ARM proposes PlanRevision DAG
             -> kernel admission -> ready TaskNode -> immutable WorkPacket
             -> worker evidence -> GateResult -> retry | replan | escalation
             -> PlanVerifierDecision -> verified terminal plan state
```

`AUTONOMOUS-PLANNING.md` is the single canonical owner for the planning object and transition
semantics. Projections in other documents link back to it. It defines `OwnerIntent`, `GoalSpec`,
`GoalSpecAmendment`, `ArmRun`, `PlanRevision`, `PlanTransition`, `TaskNode`, `WorkPacket`,
`GateResult`, `RetryDecision`, `ReplanDecision`, `Blocker`, `Escalation`,
`PlanVerifierDecision`, and the relevant command, event, lease, checkpoint, effect, route,
budget, and receipt records.

For each object it defines canonical owner, identity/version, immutable and mutable fields,
authority/privacy/route/budget/source/policy bindings, lifecycle, valid transitions, transition
authority, stale/invalid behavior, replay/idempotency, retention/audit, and relationships. The
`APQ-01` through `APQ-18` trace maps every required planning question to a normative rule, fixture,
falsifier, and Lucas seam.

Amendment compatibility is a total ordered predicate over explicit old/new node tuples, exact
digests, finite set/subset relations, integer limits, exact-equal gate requirements and a
versioned privacy-policy partial order; natural-language similarity is forbidden. Retry novelty
uses one of seven closed `NoveltyDelta` variants with exact descriptor subgrammars, a
kernel-recomputed nonempty canonical diff and a named failed condition. The kernel admits
structural novelty only; the next gate judges semantic effectiveness. Full verification and an
Owner-authorized downgrade project distinct terminal states.

The kernel, not a model, admits authoritative transitions. ARM proposals may narrow but cannot
widen an accepted goal. DAG admission rejects cycles, absent dependencies, conflicting path
ownership, and overlapping effects. Readiness is a pure predicate over the accepted plan state.
A WorkPacket is a deterministic immutable projection of one admitted TaskNode and current policy,
authority, route, budget, source, parent-version, and fence bindings.

GoalSpec amendments are Owner proposals until authenticated and accepted. Tightening authority,
privacy, egress, budget, route, publication, verifier, source, or PAUSE constraints fences future
admission immediately; in-flight external effects stop at the applicable current-policy boundary
and unresolved effects become ambiguous, never successful. A deterministic impact computation
retains unaffected work and invalidates, quarantines, cancels, or supersedes dependent revisions,
nodes, packets, leases, effects, and evidence. A stale packet or executive lease has no transition
authority.

Gate failure returns typed evidence to the ARM. Retry requires a bounded new attempt plus a
recorded novelty delta capable of changing the failed condition. Repetition without novelty is
rejected before another model turn. Exhaustion or semantic uncertainty forces replan, narrowing,
escalation, or stop according to recorded authority. Missing verifiers block. A risk-approved
downgrade binds the exact Owner/GoalSpec verifier policy and constitution digests and is never
reported as full independence. Quota exhaustion defers; it cannot enable metered spending.

Deterministic replay orders accepted events, verifies versions, digests, causation, idempotency,
leases, and fence epochs, and reproduces the exact accepted plan digest. Unknown fields, unknown
policy versions, duplicate conflicts, stale proposals, unauthenticated commands, and ambiguous
external effects fail closed.

## Strongest grounded findings

| Finding | Confidence | Competing option, failure mode, and decisive test |
|---|---|---|
| Option 2—deterministic Recursion kernel plus typed fail-closed external-loop adapters—is the narrow recommendation, not owner authority. | high boundary; medium outcome | Option 1 or a later minimal native loop may win. Lossy lifecycle translation, unfenceable writers, or a preregistered matched comparison favoring another option falsifies it. |
| SQLite supports serialized writes but does not supply Recursion's authority/fencing contract. | high | Another durable store may fit. Multi-writer discovery, corrupt-reset exposure, or failed replay/fence fixtures defeats SQLite admission. |
| Deterministic planning needs immutable accepted inputs, explicit revision/fence lineage, and kernel admission. | high contract; unproved runtime | Informal model-managed plans are simpler but permit stale mutation and ambiguous replay. M1A fixtures decide whether the minimum contract is coherent. |
| Provider-specific cache observations must remain route-specific and experimental. | high | Portable provider-neutral context remains the baseline. A pinned cross-route comparison with exposed denominators may justify a route-specific optimization. |
| Same-family review is not cross-family verification; missing verification is not a pass. | high | A purpose-bounded approved external-family review may add independence. Until then, record the gap. |
| The broad former Milestone 1 is not a lean first implementation slice. | high | M1A isolates planning schemas, validation, sanitized fixtures, and in-memory replay; any required provider/process/plugin/database effect falsifies its boundary. |

## Strongest contradictory evidence and narrowed claims

- SQLite's WAL reset-corruption correction through affected release lines contradicts any claim
  that “WAL is safe” without a version and recovery test.
- POSIX process groups, Windows Job Objects, cgroups, ConPTY, and SSH channel primitives do not
  guarantee universal descendant containment, rollback, terminal parity, or effect certainty.
- TUF, SLSA, signatures, digests, SBOMs, and transparency records establish bounded integrity or
  provenance properties, not plugin safety, semantic correctness, quota authority, or spend
  authority.
- W3C PROV, DOI metadata, Crossmark, DataCite, arXiv, and OpenAlex can establish identity,
  derivation, or status signals; none establishes scientific truth.
- Provider cache counters and controls do not establish Codex OAuth CLI behavior, subscription
  debit, savings, or cross-provider cache reuse.
- A documentation dogfood replay is not a runtime replay; v2 regression tests cannot establish a
  v3 runtime or performance result.
- No claim that v3 is optimized, lightweight in operation, quota-efficient, performance-ready,
  or superior to v2 survived as an observed result.
- The prior Muse verdict is not recoverable evidence. Sol/Luna/Terra consensus is same-family.

## Constitutional conflicts and Lucas seams

`CONTROL_PLANE.md` remains operative. These proposed rules are non-operative until Lucas resolves
them through the authoritative process:

1. current immediate PAUSE versus proposed future checkpoint, interrupt, or drain modes;
2. the current ChatGPT/Codex-OAuth planning clause versus a future provider-neutral route model;
3. Lucas-reserved control-plane, credential, spending, publication, and deployment seams versus
   any future sovereign grant administration;
4. live Git clones/project files as current project-state authority versus a future durable
   runtime-event store with Git as source evidence/projection;
5. preferred cross-family verification versus risk-approved same-family downgrade/exception; and
6. proposed exclusive ARM authorship of implementation DAGs versus the current control-plane
   statement that Hermes decomposes goals and orders dependencies.

Lucas must decide whether to ratify Option 2; the exact GoalSpec acceptance/amendment and
Head-versus-ARM DAG-authority split; any future PAUSE policy; verifier downgrade policy; sovereign
grant boundaries; provider-neutral routing; configuration merge rules; and later runtime-state
migration. M1A represents these seams as versioned bindings and fixtures and does not choose them.

## M1A verdict

[M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md) defines the bounded first future
construction milestone. It contains only pure schemas and validation, sanitized fixtures, and
deterministic in-memory replay required to demonstrate:

```text
owner intent -> accepted GoalSpec -> PlanRevision -> admitted DAG/TaskNode
-> immutable WorkPacket -> GateResult -> retry/replan/escalation
-> verified terminal plan state
```

Its seven-node construction DAG, exact future allowed paths, non-goals, 23 required fixtures,
expected results, falsifiers, and 13 machine-checkable gates are specified. The exact wire
profile is [M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md); the closed
command/event/error/digest grammar and symbolic expected sequences are in
[M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md); M1A-01 must materialize reviewed schemas and
M1A-02 must freeze literal red bundles and obtain review before reducer code. It performs no
provider call, terminal process, plugin execution, SQLite migration, publication, external effect,
or Git mutation outside its own separately authorized future implementation task. M1B contains
broader route, plugin, terminal, and scientific contracts; M1C contains runtime integration and
durability.

M1A remains a candidate for a separate owner-authorized construction task after the
PR-V3DF-20260903-05 candidate-range gates and Terra recheck pass. Its first construction node, not this campaign,
creates executable fixture bundles. M1A has not been executed. The standalone prompt is
[prompts/m1a-autonomous-planning-contract.md](prompts/m1a-autonomous-planning-contract.md).

## Source and decision discipline

The exact source revisions, licenses, locators, limitations, and revalidation triggers live in
[SOURCE-REGISTER.md](SOURCE-REGISTER.md), [REFERENCE-MATRIX.md](REFERENCE-MATRIX.md),
[R1-R17-EVIDENCE.md](R1-R17-EVIDENCE.md), and [CLAIM-LEDGER.md](CLAIM-LEDGER.md). Search snippets
and model agreement are not evidence. A source
change, affected dependency upgrade, API capability change, correction/retraction event, failed
fixture, or contradictory primary source invalidates the dependent conclusion until reverified.

Recommendations remain falsifiable and subordinate to Lucas. The final independent adjudicator's
blocking dissent is preserved in the campaign artifact. The PR-V3DF-20260903-05 correction must
pass the exact procedure in [VALIDATION.md](VALIDATION.md) and receive the requested Terra recheck
before this document can move to evidence-reconciled.
