---
title: R-R — Long-horizon autonomy and scheduling
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-R — Long-horizon autonomy and scheduling

This is a long-horizon-autonomy and scheduling handoff for accepted Owner decisions D-018, D-019,
D-022, D-024 and D-025, with D-031 as a constraint and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-P](R-P-prompt-injection-and-untrusted-input-defense.md), the untrusted-input handoff, and on
[R-Q](R-Q-durable-memory-and-knowledge-architecture.md), the durable-memory handoff: R-P governs
what an autonomous run may trust and R-Q governs what it may remember, while R-R designs how a goal
is decomposed, replanned and scheduled across a long horizon under hard stopping rules. It extends
the planning slice recorded in [PLANNING.md](../../PLANNING.md) and
[AUTONOMOUS-PLANNING.md](../../AUTONOMOUS-PLANNING.md) rather than restating it, and it consumes
the scheduler and supervision gaps of DS-29 and DS-30. It must extend, not restate, the
lease/authority semantics those lanes share. It does not select a language, store, framework,
scheduler, workflow engine or vendor, does not qualify any route, and executes no provider call.

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

- The object of study is **long-horizon autonomy without a standing autonomous executive**:
  goal decomposition, replanning, unattended operation, self-scheduling, budgets, progress
  measurement, human-in-the-loop triggers and safety floors — all under the Owner decisions that
  forbid a self-directed executive tier.
- D-025 is the controlling decision: 24/7 autonomous research is an optional, off-by-default,
  budgeted plugin with explicit sources, cadence, stopping conditions and promotion authority. It
  is not a standing executive and cannot self-activate or self-approve. This lane designs the
  mechanics such a plugin needs and must not smuggle in the executive that D-025 and
  [ANCHOR.md](../../../../ANCHOR.md) place out of scope ("any standing autonomous executive that
  decomposes and assigns work on its own" is explicitly not this year).
- D-018 makes Recursion a first-class native harness *and* a first-class wrapper over the wider
  harness ecosystem whose purpose is to remove lock-in and cut quota/usage burn; long-horizon work
  must therefore run across harnesses without holding credentials it was not granted and must not
  assume one vendor's scheduling or automation feature.
- D-019 ships every capability as an **opt-in plugin or profile** rather than a default:
  scheduling, unattended runs and background continuation are off unless enabled, and the disabled
  path must be inert (zero wakeup, zero model call, zero egress, zero effect).
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain` — across configuration, the formal model and the broker. A long-horizon
  run must map to that vocabulary: what each Stop does to a pending schedule, an in-flight step, a
  sleeping wakeup and a running worker; and the honest distinction between "asked to stop" and
  "observed stopped".
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. Resumption after a crash or a paused
  horizon must restore authority and evidence honestly rather than fabricate progress.
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: productivity, progress
  and cost figures are reported as measured facts, never as vendor-intent narratives.
- Non-negotiable direction this lane must respect: workers are bounded executors with bounded step
  leases; authority is computed at effect-admission and cannot be widened by a schedule, a retry or
  an elapsed deadline; live provider/host/spend actions are human-gated; a missing counter is
  `unknown`, never zero; and every recommendation carries a competing option, a decisive falsifier
  and an explicit non-proof.
- Prior comparison coverage to extend, not reinvent: the goal/GoalSpec decomposition of
  [PLANNING.md](../../PLANNING.md) and [AUTONOMOUS-PLANNING.md](../../AUTONOMOUS-PLANNING.md), the
  bounded step leases of DS-15, the multi-project supervision memory of DS-30, the scheduler/daemon
  crash-recovery gap G-30, the review-throughput rationing rule of
  [ANCHOR.md](../../../../ANCHOR.md), and the HITL pre-effect boundary of DS-32. External
  autonomous-agent and workflow orchestrators are prior art cited from public documentation, not
  endorsed or selected components.
- Evidence status: no long-horizon run, self-scheduling daemon, budget controller, replanner or
  HITL fixture has been implemented or measured by Recursion for this lane. Every progress,
  budget, stopping and safety statement below is to be established from public source, documented
  behavior and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **long-horizon autonomy and scheduling design candidate** for Recursion.
The lane specifies goal decomposition and bounded replanning; unattended operation and
self-scheduling scoped to a plugin; explicit budgets and stopping, escalation and promotion rules;
human-in-the-loop triggers and the pre-effect approval boundary; progress measurement that is
honest and hard to game; and safety floors that distinguish frontier long-horizon work from a
runaway loop. It defines what a bounded, optionally enabled autonomy plugin may do, and states
explicitly that it is not a standing autonomous executive and cannot self-activate, self-approve
or self-widen. It delivers a design candidate with competing options, decisive falsifiers and an
explicit statement of what it does not prove, plus provider-free fixtures. It does not select a
language, store, framework, scheduler, workflow engine or vendor, does not qualify any route, and
executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, scheduler, workflow engine, queue, runtime or
vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024, D-025 or D-031.
Treat every named external autonomous-agent or workflow product as prior art cited from public
documentation, not as an endorsed or selected component. No provider, model or account call is
made; no unattended run is started; no credential or account is touched. **Do not design, imply or
endorse a standing autonomous executive that decomposes and assigns work on its own**; that is
explicitly out of scope. Do not claim that a schedule, deadline, retry counter or plugin flag
confers authority, approves an effect or promotes a result. Do not assert a measured productivity,
progress, stopping or cost advantage that was not measured; record it `unknown`. Hidden
chain-of-thought is neither requested nor displayed.

## Inputs to read

None from this repository: the rescope, the planning slice, the authority and lease semantics, the
supervision gap and the review-throughput rationing rule are summarized in `## Baked context`
above, and no repository, connector or private-source access is assumed. The session must, however,
retrieve the public documentation it cites — the public literature on long-horizon and open-ended
agent autonomy, on progress estimation and reward hacking, on scheduling and job-orchestration
patterns with stopping and backoff, on human-in-the-loop approval and pre-effect mediation, and the
documented behavior of provider rate limits, budgets and usage accounting — and pin each claim to
a URL and retrieval date.

## Research questions

### Goal decomposition and replanning

1. What is the bounded decomposition model that turns a goal into a work tree of steps under a
   GoalSpec, and how is each step tied to a bounded lease, an acceptance gate and an explicit
   authority scope so that a plan is a proposal and never a grant?
2. How is replanning bounded and auditable — when a step fails, when new evidence invalidates a
   plan, when a dependency changes — and what prevents an unbounded replanning loop that consumes
   budget without progress?
3. What is the relationship between the plan, the canonical plan revision and any remembered plan
   (R-Q), so that a replan does not silently overwrite an accepted decision or reuse a stale
   summary as authority?
4. What is the competing option to hierarchical decomposition (for example a flat task queue or a
   single agent with a scratchpad), and what decisive falsifier would show decomposition is or is
   not worth its coordination cost?

### Unattended operation and self-scheduling

5. What does "unattended" honestly mean for a run: which events may wake it (timer, external
   signal, queued work, dependency completion), what may it do with no human present, and what must
   it never do without a human (live provider calls, host actions, spend, publication, merge)?
6. How is self-scheduling bounded — cadence, maximum concurrent runs, backoff, jitter, quiet hours,
   budget ceiling — so that a plugin can run continuously without becoming an unbounded background
   process, and how is the disabled path inert?
7. How does a scheduled wakeup interact with the D-022 Stop vocabulary: what happens to a sleeping
   timer, a pending retry and an in-flight step under Aggressive/Full/Lazy and under
   `checkpoint`, `interrupt` and `drain`, and how is "asked to stop" distinguished from "observed
   stopped"?
8. How is cross-harness scheduling kept provider-neutral and credential-free under D-018 and
   D-021, so an unattended run delegates to a user-authenticated harness rather than becoming a
   credential relay?

### Budgets, stopping and escalation

9. What budgets must bind a long-horizon run — wall-clock, token/model, monetary/quota, tool-call,
   effect, artifact and review — and how is each counted honestly with `unknown` kept distinct
   from zero when a counter is unavailable?
10. What stopping conditions are required — goal met and independently verified, budget exhausted,
    no-progress detected, safety floor tripped, authority revoked, dependency blocked, human
    interrupt — and who or what is authorized to declare each?
11. What escalation path exists when a run cannot proceed: what it reports, to whom, with what
    evidence, and how it avoids both silent drift and an alert loop, given that an implementer's
    own PASS is never acceptance?
12. What is the rule that a schedule or elapsed deadline never widens authority, approves an
    effect or promotes a result — promotion remains a human or independent-verification act — and
    how is that rule tested?

### Human-in-the-loop triggers and safety floors

13. What are the mandatory HITL triggers (irreversible effect, spend, publication, merge,
    credential or authority change, ambiguous intent, repeated failure, budget near-exhaustion),
    and how is each enforced at the pre-effect mediation boundary rather than by convention?
14. What safety floors must halt a run regardless of apparent progress — authority revocation,
    privacy or egress violation, containment failure, untrusted-input refusal storm, Stop issued —
    and what is the fail-closed behavior of each?
15. How does a long-horizon run avoid runaway behaviors — retry storms, fan-out explosion,
    self-reinforcing subgoals, objective drift, resource blow-up, quota burn without value — and
    what negative trace or tripwire detects each before it becomes an incident?
16. What progress measurement distinguishes real verified progress from activity, repetition or
    optimistic self-report, and how is it tied to accepted evidence rather than the model's own
    claim?

### What makes autonomy frontier versus runaway, and fixtures

17. What concretely separates **frontier long-horizon autonomy** from a **runaway loop**: verified
    progress per unit cost, stable authority, bounded fan-out, a decidable stopping rule, honest
    accounting and a human-gated effect path — and how is each property measured rather than
    asserted?
18. What provider-free fixtures must accept or reject: a bounded decomposition, a replan after
    failure, a budget-exhaustion stop, a no-progress stop, an unauthorized-effect refusal, a Stop
    during a sleeping schedule, a crash-and-resume continuity case, a disabled-path inertness soak
    and a HITL-trigger case — and what is the exact pass/fail predicate for each?
19. How do the fixtures prove that no schedule, retry, deadline or plugin flag confers authority or
    approves an effect, that a Stop reaps pending schedules and in-flight steps, that a crash resume
    preserves authority and evidence honestly, and that no run creates a standing executive or a
    second portfolio executive — using synthetic events only, with no provider call?
20. How is each result classified as source-documented, locally observed, inferred or `unknown`,
    and what does the suite not establish — for example no measured productivity gain, no real
    unattended-run safety proof and no claim about any provider's rate-limit or automation
    behavior?

## Deliverable

A long-horizon autonomy and scheduling design candidate containing: a goal-decomposition and
bounded-replanning section tied to leases, gates and authority scopes; an unattended-operation and
self-scheduling section covering wake events, bounded cadence and D-022 Stop interaction; a
budgets, stopping and escalation section with honest counters, named stopping conditions and a rule
that a schedule never confers authority; a human-in-the-loop and safety-floor section enforced at
the pre-effect mediation boundary; a progress-measurement section distinguishing verified progress
from activity; and a provider-free fixture suite for decomposition, replanning, budget and
no-progress stops, unauthorized-effect refusal, Stop-during-schedule, crash-and-resume continuity,
disabled-path inertness and HITL triggers. The candidate explicitly states that it is not a
standing autonomous executive and cannot self-activate, self-approve or self-widen. Each
recommendation names a competing option, a decisive falsifier and what it does not prove. No
language, store, framework, scheduler, workflow engine or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, scheduler, workflow engine, queue,
  runtime or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No standing autonomous executive that decomposes and assigns work on its own; no self-activation,
  self-approval or self-widening (D-025, ANCHOR).
- No assertion that a schedule, deadline, retry counter or plugin flag confers authority, approves
  an effect or promotes a result.
- No live provider, host or spend action without a fresh, reviewed human admission; unattended
  operation may not perform them.
- No provider, model, credential or account call; no unattended run started; every fixture is
  synthetic and provider-free.
- No claim of a measured productivity, progress, stopping or cost advantage where no measurement
  exists; those cells stay `unknown`.
- No reopening of D-018, D-019, D-022, D-024, D-025 or D-031, and no vendor-sabotage narrative
  (D-031).
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The decomposition and replanning section defines a bounded work tree under a GoalSpec, ties each
  step to a lease, gate and authority scope, and bounds replanning against unbounded loops.
- The unattended-operation section defines honest wake events and bounded self-scheduling, and maps
  a sleeping schedule, pending retry and in-flight step to the D-022 Aggressive/Full/Lazy,
  `checkpoint`, `interrupt` and `drain` vocabulary with "asked to stop" distinct from "observed
  stopped".
- The budgets and stopping section names wall-clock, token, monetary/quota, tool-call, effect,
  artifact and review budgets, keeps `unknown` distinct from zero, and lists goal-met,
  budget-exhausted, no-progress, safety-floor, authority-revoked, dependency-blocked and
  human-interrupt stopping conditions.
- The HITL and safety-floor section enumerates mandatory triggers and enforces them at the
  pre-effect mediation boundary, with fail-closed behavior for authority revocation, privacy or
  egress violation, containment failure and Stop.
- The candidate states that no schedule, deadline, retry or flag confers authority, approves an
  effect or promotes a result, and that it is not a standing autonomous executive and cannot
  self-activate, self-approve or self-widen.
- The progress-measurement section distinguishes verified progress from activity and self-report
  and ties progress to accepted evidence.
- The provider-free fixture suite specifies predicates for decomposition, replanning, budget and
  no-progress stops, unauthorized-effect refusal, Stop-during-schedule, crash-and-resume
  continuity, disabled-path inertness and HITL triggers, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, scheduler, workflow engine or vendor is selected and no route is
  qualified.
- The candidate explicitly states what it does not establish: no measured productivity gain, no
  real unattended-run safety proof, no provider rate-limit or automation claim, no route
  qualification and no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.
