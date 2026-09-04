---
title: Recursion v3 architecture-proof and planning-baseline result
status: evidence-reconciled-construction-baseline-with-frontier-research
last-updated: 2026-09-03
source-checkpoint: 672081fc1874ab9b7a41a14ca61adc60ecd71c95
source-baseline: 98113d6c6d3debe2a4d207c51bb1780f7356d714
frontier-campaign-base: a97d5181ee413b87597ea58523708bb9a53f750b
---

# Recursion v3 architecture-proof and planning-baseline result

This is the durable synthesis of the 2026-09-03 evidence-closure and autonomous-planning
campaign. It is a documentation result. It does not prove that a v3 runtime exists, authorize
implementation, change the constitution, configure a provider, permit spending,
or authorize publication, deployment, service changes, or a private canary.

The initial campaign did not ratify Option 2. Lucas subsequently ratified it and sole Recursion
canonical ownership in `OR-018` and `OR-019`, and authorized the future PAUSE/verifier amendment
proposal in `OR-020`. Those later Owner decisions select architecture but do not supply runtime
proof or make the docs-only amendment operative.

The exact campaign inputs, immutable demonstration `GoalSpec`, plan revisions, task DAG,
worker packets, gates, and disposition are in
[AUTONOMOUS-PLANNING-CAMPAIGN.md](AUTONOMOUS-PLANNING-CAMPAIGN.md). The canonical proposed
planning semantics are in [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md). The independently
reconstructed evidence for every R1-R17 lane is in
[R1-R17-EVIDENCE.md](R1-R17-EVIDENCE.md).

The 2026-09-03 frontier-harness continuation is independently inspectable in
[FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md](FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md) and
[FRONTIER-HARNESS-EVIDENCE.md](FRONTIER-HARNESS-EVIDENCE.md). It added exact code-path,
terminal, plugin/frontend, systems-performance and evaluation-method evidence without changing
the planning-only M1A scope or producing runtime proof.

The second continuation is recorded in
[FRONTIER-HARNESS-RESEARCH-TRANCHE-2.md](FRONTIER-HARNESS-RESEARCH-TRANCHE-2.md) and its
[evidence packet](FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md). It adds formal-model,
neutral-kernel, persistence/IPC, process-broker, plugin/frontend, cache/context, evaluation and
release contracts and the exact
[constitutional amendment proposal](CONSTITUTIONAL-AMENDMENT-PROPOSAL.md).

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
| `WP-V3DF-301` | `gpt-5.6-terra`, `xhigh` | Authority adjudication | Conditional support; added complete prompt traceability, exact downgrade binding, and the then-sixth constitutional conflict. OR-016 later created a seventh product-identity conflict. |
| `WP-V3DF-302` | `gpt-5.6-terra`, `xhigh` | Final evidence/readiness adjudication | Preserved successive dissent on five candidates, then returned `PASS` on exact semantic candidate `640a6d2c17c6f3cd9b360a93452dca0b30be1785` after source, grammar, wire, policy and retry closure; high/0.94 confidence, same-family only, no runtime proof. |

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
| Option 2—deterministic Recursion kernel plus typed fail-closed external-loop adapters—is the Owner-ratified architecture, not measured superiority. | high authority; medium implementation outcome | A hard invariant outside the boundary, lossy lifecycle translation or unfenceable writer requires an Owner amendment; measured components inside the boundary remain selectable. |
| SQLite supports serialized writes but does not supply Recursion's authority/fencing contract. | high | Another durable store may fit. Multi-writer discovery, corrupt-reset exposure, or failed replay/fence fixtures defeats SQLite admission. |
| Deterministic planning needs immutable accepted inputs, explicit revision/fence lineage, and kernel admission. | high contract; unproved runtime | Informal model-managed plans are simpler but permit stale mutation and ambiguous replay. M1A fixtures decide whether the minimum contract is coherent. |
| Provider-specific cache observations must remain route-specific and experimental. | high | Portable provider-neutral context remains the baseline. A pinned cross-route comparison with exposed denominators may justify a route-specific optimization. |
| Same-family review is not cross-family verification; missing verification is not a pass. | high | A purpose-bounded approved external-family review may add independence. Until then, record the gap. |
| The broad former Milestone 1 is not a lean first implementation slice. | high | M1A isolates planning schemas, validation, sanitized fixtures, and in-memory replay; any required provider/process/plugin/database effect falsifies its boundary. |
| The privileged kernel should be smaller than the complete object catalog: deterministic admission/reduction, authority/budget/privacy/fence checks, packet derivation, effect classification, replay and publication gates only. | medium-high recommendation; unproved implementation | A fuller native loop may later win. Typed adapters fail this boundary if they cannot preserve identity/effect/evidence invariants across materially different engines. |
| Harness effects require fixed-model component ablations and owner-review measurement. | high methodology; no local outcome | Leaderboards and agent count confound interface, planning, delegation, verification, retry, budget and contamination. The `EXP-FHAR-07/08` matched design decides local benefit. |
| Disabled optional capabilities must execute no implementation path. | high contract; unmeasured | Manifest-only discovery may still have bounded metadata cost. `EXP-FHAR-09/12` use import/network/process/context/quota traps and fenced reload to decide conformance. |

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
- Rust, Go, CPython, SQLite, JSONL, binary IPC, terminal libraries and plugin isolation remain
  candidates. Static mechanisms, line counts and dependency manifests do not select them.
- Agentless and delegation-contract evidence contradict monotonic “more autonomy is better”
  claims: simpler staging may compete, while better evidence can add tokens/time without a
  correctness gain.
- The prior Muse verdict is not recoverable evidence. Sol/Luna/Terra consensus is same-family.

## Constitutional conflicts and Lucas seams

`CONTROL_PLANE.md` remains operative. `OR-018` through `OR-020` resolve the target direction, but
these rules remain non-operative until the exact amendment is applied through the authoritative
process:

1. the current Hermes-specific Head identity versus the Recursion-owned `Head` selected in
   OR-016;
2. current immediate PAUSE versus proposed future checkpoint, interrupt, or drain modes;
3. the current ChatGPT/Codex-OAuth planning clause versus a future provider-neutral route model;
4. Lucas-reserved control-plane, credential, spending, publication, and deployment seams versus
   any future sovereign grant administration;
5. live Git clones/project files as current project-state authority versus a future durable
   runtime-event store with Git as source evidence/projection;
6. preferred cross-family verification versus risk-approved same-family downgrade/exception; and
7. proposed exclusive ARM authorship of implementation DAGs versus the current control-plane
   statement that Hermes decomposes goals and orders dependencies.

The drafted amendment now covers Recursion ownership, Head-versus-ARM authority, future PAUSE and
verifier downgrade classes. Lucas still must decide its application timing, sovereign grant and
audit-erasure boundaries, provider-neutral live routing, configuration merge rules, and later
runtime-state migration. M1A represents these seams as versioned bindings and fixtures and does
not activate them.

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

M1A is documentation-ready for a separate owner-authorized construction task: the exact
candidate-range gates and targeted Terra recheck passed. M1A-01 must materialize/review the
strict schemas and M1A-02, not this campaign, creates executable fixture bundles before reducer
code. M1A has not been executed. The standalone prompt is
[prompts/m1a-autonomous-planning-contract.md](prompts/m1a-autonomous-planning-contract.md).

## Source and decision discipline

The exact source revisions, licenses, locators, limitations, and revalidation triggers live in
[SOURCE-REGISTER.md](SOURCE-REGISTER.md), [REFERENCE-MATRIX.md](REFERENCE-MATRIX.md),
[R1-R17-EVIDENCE.md](R1-R17-EVIDENCE.md), and [CLAIM-LEDGER.md](CLAIM-LEDGER.md). Search snippets
and model agreement are not evidence. A source
change, affected dependency upgrade, API capability change, correction/retraction event, failed
fixture, or contradictory primary source invalidates the dependent conclusion until reverified.

Recommendations remain falsifiable and subordinate to Lucas. Every intermediate adjudicator
dissent and failed gate is preserved in the campaign artifact. The exact semantic candidate
passed [VALIDATION.md](VALIDATION.md) and its targeted Terra recheck; that makes this an
evidence-reconciled documentation baseline, not a runtime or performance result. The later Owner
ratification is recorded separately and does not change what the campaign proved.
