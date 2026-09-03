---
title: Recursion v3 executive model
status: accepted-direction-with-open-research
last-updated: 2026-09-03
---

# Recursion v3 executive model hypothesis

> **Proposed post-amendment model.** These role definitions are the product target recorded by
> the Owner; they are not the operative repository constitution. Until Lucas ratifies and records
> a constitutional amendment, Hermes retains the executive authority assigned by
> `CONTROL_PLANE.md`, and proposed ARM-exclusive DAG authorship is inert design material.

## Actor definitions

### Recursion Head

The Recursion-owned `Head` is the single accountable portfolio executive beneath Lucas. It:

- preserves owner intent and portfolio context;
- compiles GoalSpec drafts from accepted owner intent and strategic constraints;
- starts, monitors, pauses, resumes, replaces, and closes ARM runs;
- allocates aggregate capacity and review attention across goals;
- evaluates semantic escalations and proposes amendments;
- never edits product code or bypasses the deterministic actuator.

### ARM executive

An ARM is a durable executive bounded to one versioned GoalSpec. It:

- orients from exact repository and canonical state;
- creates and maintains the implementation DAG;
- delegates bounded research, implementation, testing, review, and integration work;
- chooses among only the routes and resources permitted by its inherited policy;
- responds tactically to evidence and failures;
- checkpoints its state and reports progress or blockers upward;
- cannot create unrelated goals or implicitly expand authority through planning or delegation;
  merge, deployment and other high-impact capabilities exist only when the exact grant/GoalSpec
  and operative constitution allow them. A separately explicit maximum `sovereign`
  `grant-admin` capability may authorize a receipt-backed grant mutation; it is not inherited by
  ordinary ARMs or children.

The exact Head/ARM proposal, decision and transition boundary is canonical in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md#authority-and-responsibility).

An ARM normally exposes an addressable conversation so the owner can speak with it directly.
One ARM per repository is a likely configuration default, not an identity rule: ARM identity is
bound to a GoalSpec, and a goal may be narrower than or span more than one repository. Direct
conversation does not bypass Head monitoring or turn chat history into canonical state. See
[INTERACTION-SURFACES.md](INTERACTION-SURFACES.md).

In a shared multi-ARM workflow, Head owns the overall goal, membership, authority envelope,
conflict resolution, ARM lifecycle and strategic model escalation. Head may issue a bounded,
expiring coordination lease to one named ARM for one workflow step. That lease permits routing
messages and proposing transitions inside the step; it does not create another executive tier,
admit new members, widen authority or settle cross-goal conflicts.

### Delegated agent

A delegated agent receives one immutable WorkPacket with a repository/worktree, allowed paths, non-goals, capabilities, resource envelope, budget source, output contract, and machine-checkable gate. It does not reinterpret the parent goal.

## Logical identity is not a model

These events must remain distinct:

- **model escalation:** the same logical actor selects a different approved model;
- **provider failover:** the same segment uses another authorized delivery route;
- **delegation:** an actor creates a bounded child actor or harness session;
- **authority escalation:** a question moves from worker to ARM to Head to Lucas;
- **executive replacement:** a new lease holder resumes the same logical role from a validated checkpoint.

Telemetry, budgets, context, and audit records must never collapse these into a generic "model changed" event.

## Profiles and runs

`ExecutiveProfile` is reusable configuration: task-domain strengths, allowed model suites, default planning depth, delegation limits, context strategy, review policy, and resource posture.

`ArmRun` is ephemeral in scope but durable in state: one goal version, one active executive lease, exact authority, current plan, delegated descendants, capacity reservations, checkpoint lineage, open blockers, and terminal evidence.

This separation preserves project personalization without creating an immortal project conversation whose stale assumptions and context grow indefinitely.

## Model policy

Both Head and ARM use configurable model suites rather than a universal ladder. Candidate suites may include architecture, security, backend, frontend, mechanical refactoring, documentation, compaction, integration, and verification.

Routing is quality-first adaptive by default for the private deployment:

1. Establish the task's quality floor, privacy class, tool needs, and continuity risks.
2. Select the least scarce eligible route expected to meet that floor.
3. Prefer an existing healthy session when its context affinity materially reduces work.
4. Hold a route stable between safe checkpoints.
5. Escalate after uncertainty, repeated failure with new evidence, verifier disagreement, or task-complexity growth.
6. Do not change billing basis or consume an unapproved pool implicitly.

Users may choose `quality-wait`, `adaptive`, `throughput`, `cost-first`, `maximum`, or custom policies.

Lucas's 2026-09-03 product ruling permits Head and ARM planning to use any route inside an
explicit owner-approved model/provider/account/capacity-pool envelope. Route selection never
widens the GoalSpec, privacy, credentials, spending or tool grants. This product ruling requires
a reviewed amendment to the current provider-specific constitutional clause before it changes
the private deployment; it is not authority to edit provider or authentication configuration.

## Safe checkpoints

A checkpoint is machine-determined, not merely asserted by the model. It requires:

- no unbounded or partially applied external side effect;
- repository and worktree state recorded exactly;
- current task, last completed operation, and next intended operation recorded;
- child leases and process state known;
- consumed usage and remaining authority reconciled;
- context capsule validated and rehydratable;
- ordinary replacement or configuration changes allow an atomic command to reach its bounded transaction boundary;
- PAUSE follows the operative constitution-policy version; representing a future policy does not
  select it, and any outcome whose commit status is ambiguous is quarantined until reconciliation.

Ordinary model/config changes apply at the next checkpoint. A forced swap requests the earliest valid checkpoint. Emergency kill is separate and may sacrifice the in-flight operation to contain a compromised run.

## PAUSE policy direction

The product direction proposes configurable pause aggressiveness rather than one universal
behavior. The kernel, not the model, would select an owner-approved policy and record its version:

- `checkpoint` — proposed future ordinary default: admit no new operation, let the current bounded
  operation reach its next mechanically safe checkpoint, then pause;
- `interrupt` — request immediate cancellation of interruptible work, preserve atomic state and
  quarantine ambiguous effects;
- `drain` — admit no new work but allow explicitly enumerated in-flight work classes to finish;
  this is unsuitable as an implicit default for publication, deployment or new remote effects;
- emergency stop — separate break-glass behavior that blocks new effects immediately and may
  sacrifice in-flight work.

The current `CONTROL_PLANE.md` immediate halt is the only operative profile. The future values
remain separately representable but non-operative until a reviewed constitutional amendment.
The canonical state/fence behavior is in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md#pause-and-ambiguous-effects).

## Verifier independence recommendation

Verification is risk scaled. The proposed starting tiers are:

1. **Mechanical:** deterministic gate re-execution; a model adds no authority.
2. **Routine:** clean separate verifier task/session with no implementer persuasion; the same
   strong model or provider may be acceptable.
3. **Material:** clean context plus a different capable model or family when eligible, exact
   candidate binding and deterministic gates.
4. **Constitutional/high-impact/release:** independent provider or family where eligible,
   independent gate execution/environment, and owner approval for irreversible authority,
   credentials, spend, publication or deployment effects.

Unavailable diversity is disclosed. Routine work may use a documented downgrade when its
risk policy permits it. Releases, security-sensitive work, control-plane changes and
irreversible external effects block unless Lucas explicitly approves a recorded exception.
Missing or weaker verification never becomes a pass. Research must measure which separation
dimensions find materially different defects and define the exact exception receipt.

## Capacity exhaustion

The following is proposed future capacity behavior and does not weaken current PAUSE or spending
authority. When subscription capacity is exhausted mid-task:

- admit no new model turn on that pool;
- request a checkpoint only where the operative policy explicitly allows it; under current PAUSE,
  no exception for a final model turn is implied;
- record repository state and a resumable checkpoint;
- do not infer permission to finish the entire plan;
- use metered fallback only when the parent goal explicitly carries that authority;
- treat the default approved metered amount as one aggregate parent-goal budget, not a per-task allowance;
- if fallback spending was activated solely by subscription exhaustion, end that fallback authority with the originating task; otherwise it expires with the parent goal.

The precise enforcement mechanism for "already-started final turn" must be researched per harness because many CLIs expose only process/session boundaries, not model-turn internals.

## Refusal and continuity

Provider refusal is a typed outcome, not automatically proof of malicious intent or model incapacity. Recursion may offer configurable cross-family retry for suspected false positives, but public installations default it off to avoid unexpected quota use. Retries remain inside the same GoalSpec, privacy, egress, permission, and budget boundaries. Recursion must not describe or implement model switching as a way to defeat a legitimate safety or legal boundary.

Refusals produce:

- a normal telemetry event when recovery succeeds;
- an operator alert when work is blocked, policy may be incompatible, or repeated fallback consumes meaningful capacity;
- escalation to Head when semantic reframing or authority review is needed.

## Executive lease and split brain

Exactly one actor may hold the decision lease for a given Head or ArmRun at a time. Advisory models may produce analyses, but only the lease holder may propose the next authoritative plan transition. Replacement requires a validated capsule, lease transfer event, and unchanged authority envelope.

The authoritative lease, stale-transition and route-replacement rules are canonical in
[AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md).

## Open questions

- Should Head and ARM share one native loop implementation or use distinct optimized loops?
- How should an ARM expose native nested delegation from Cursor, Codex, an optional Hermes adapter, or OpenCode without losing descendant lineage?
- Which events are stable enough to become the v3 public executive protocol?
- When is a long-lived provider session more valuable than a fresh session with a compact capsule?
- How should planning models be authorized under a future provider-neutral amendment to the current constitution?
- On PAUSE or revocation, which classes of already-started operation may finish, which must be killed, and which outputs must be quarantined?
