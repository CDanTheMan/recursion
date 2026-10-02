---
title: R-S — Adaptive optimization and outcome learning
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-S — Adaptive optimization and outcome learning

This is an adaptive-optimization and outcome-learning handoff for accepted Owner decisions D-018,
D-019, D-022, D-024 and D-031, with the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-O](R-O-performance-and-configurability-engineering.md), the backend-performance handoff, and on
[R-R](R-R-long-horizon-autonomy-and-scheduling.md), the long-horizon-autonomy handoff: R-O fixes
what performance and configurability must measure and R-R bounds unattended operation, while R-S
designs how Recursion may *learn* routing, prompt, tool and compaction policies from measured
outcomes without ever becoming unpredictable or unauthorizable. It extends the routing and
telemetry research recorded in [ROUTE-CAPABILITIES.md](../../ROUTE-CAPABILITIES.md) and
[TELEMETRY.md](../../TELEMETRY.md) and the quota measurement spec of
[R-D](../dot-research-20261002/R-D-quota-efficiency-measurement.md), and it consumes the routing
and delegation gaps of DS-11 and the telemetry-accounting contract of DS-26. It must extend, not
restate, the honest-counter and authority semantics those lanes share. It does not select a
language, store, framework, model, routing algorithm, bandit or vendor, does not qualify any
route, and executes no provider call.

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

- The object of study is **learning operational policies from measured outcomes**: which route,
  model, prompt shape, tool choice and compaction policy to use for a task, adapted from observed
  cost, latency, quality, quota and correctness rather than from vendor claims or model consensus.
  The learning target is policy, not authority: an adapted policy may move work between routes but
  can never widen a capability grant, approve an effect or change what is authorized.
- D-018 makes Recursion a first-class native harness *and* a first-class wrapper over the wider
  harness ecosystem whose purpose is to remove lock-in and cut quota/usage burn; adaptivity is one
  means to that end and must stay route-neutral, portable and reversible rather than overfitting
  one provider.
- D-019 ships every capability as **opt-in plugin or profile** and never by default: adaptation is
  off unless explicitly enabled, and the disabled path must be inert (zero measurement call, zero
  model call, zero policy write, zero network egress). A conservative static policy is the
  default.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. Adaptation must be interruptible and checkpointable: what a Stop does to
  an in-flight experiment, a pending policy update and an exploration arm, and what "applied"
  versus "reverted" honestly means.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. A learned policy change must not corrupt
  continuity, silently re-route an authorized task or erase the evidence that justified a prior
  decision.
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: every routing, cost and
  quality comparison is reported as a measured fact with its provenance and uncertainty, never as a
  vendor-intent narrative.
- Non-negotiable direction this lane must respect: counters are provenance-qualified and a missing
  counter is `null`/`unknown`, never `0` (DS-26); every recommendation carries a competing option, a
  decisive falsifier and an explicit non-proof; no language, store, framework, model or vendor is
  selected; authority is computed at effect-admission and is never a function of a metric.
- Prior comparison coverage to extend, not reinvent: the task-specific route suites and
  first-review-acceptance endpoint of DS-11, the two-ledger accounting contract of DS-26, the
  performance and ablation discipline of DS-10 and R-O, the quota/lock-in measurement
  preregistration of R-D, and the context/cache economics of
  [CONTEXT.md](../../CONTEXT.md). Published bandit, online-learning and auto-tuning results are
  prior art cited from public sources, not endorsed or selected methods.
- Evidence status: no adaptive policy, bandit, reward model, offline learner, shadow evaluator or
  regression guard has been implemented or measured by Recursion for this lane. Every benefit,
  exploration-cost, non-stationarity and reward-hacking statement below is to be established from
  public source, documented behavior and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **adaptive-optimization and outcome-learning design candidate** for
Recursion. The lane specifies what may adapt (routing, prompt, tool and compaction policies) and
from what measured outcome evidence; the distinction between offline adaptation and online
adaptation with exploration cost; non-stationarity and staleness handling; hard guardrails and
floors that adaptation may never cross; anti-reward-hacking requirements; the rule that adaptation
is always optional and off by default; and decisive falsifiers for both no-benefit and regression.
It delivers a design candidate with competing options, decisive falsifiers and an explicit
statement of what it does not prove, plus provider-free fixtures. It does not select a language,
store, framework, model, routing algorithm, bandit, optimizer or vendor, does not qualify any
route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, model, routing algorithm, bandit, optimizer, tuner or
vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024 or D-031. Treat
every named learning method, auto-router or evaluation benchmark as prior art cited from public
documentation, not as an endorsed or selected component. No provider, model or account call is
made; no live experiment is run; no credential or account is touched. Do not claim that a learned
policy improves quality, cost or quota without a preregistered measurement and an independent
result; do not claim that adaptation confers authority or approves an effect. Do not present a
vendor-intent narrative; every comparison is a measured fact with uncertainty (D-031). Do not
assert a reward-hacking immunity, an exploration bound or a non-stationarity guarantee that was
not measured; record it `unknown`. Hidden chain-of-thought is neither requested nor displayed.

## Inputs to read

None from this repository: the rescope, the route/telemetry contracts, the performance discipline
and the quota measurement specs are summarized in `## Baked context` above, and no repository,
connector or private-source access is assumed. The session must, however, retrieve the public
documentation it cites — the public literature on contextual bandits and online/offline learning
with exploration and non-stationarity, on reward hacking and specification gaming, on auto-tuning
and cost-aware routing, on shadow and A/B evaluation and on guardrails and hard constraints in
learned systems, plus the documented behavior of provider rate limits, budgets and usage
accounting — and pin each claim to a URL and retrieval date.

## Research questions

### What may adapt, and from what evidence

1. Which policies may adapt — route/provider/model choice, prompt and context shape, tool or
   harness selection, compaction and cache policy, fan-out and retry — and which must remain fixed
   for authority, security, privacy or auditability reasons?
2. What measured outcome signals feed adaptation — task acceptance, first-review acceptance,
   false-green rate, human correction, tokens, latency, quota debit, monetary cost, rework,
   retry and review minutes — and how is each provenance-qualified so `unknown` is never read as
   zero?
3. How is the learning objective aligned with the accepted objective (correctness,
   authorization, recoverability, responsiveness, subscription efficiency, completion) rather than
   a convenient proxy, and what is the competing option of a hand-tuned static policy?
4. What is the rule that adapted policy is a proposal applied to routing only, and that no learned
   parameter can widen authority, approve an effect, alter privacy scope or change an acceptance
   gate?

### Offline versus online adaptation and exploration cost

5. What separates offline adaptation (learn from logged outcomes, evaluate, then promote a policy)
   from online adaptation (adapt during live operation), and what is the competing option, hidden
   cost and decisive falsifier for each?
6. What exploration is required for online learning, what cap bounds the extra spend/latency/quota
   it costs, and how is exploration denied on live, irreversible or human-gated actions?
7. How is a policy promoted — shadow mode, canary, limited rollout, A/B, human approval — and who
   is authorized to promote it, given that an implementer's own PASS is never acceptance?
8. How does an in-flight experiment, exploration arm or pending policy update map to the D-022
   Stop vocabulary, and what does "applied" versus "reverted" honestly mean for a learned policy?

### Non-stationarity, staleness and continuity

9. How is non-stationarity handled — provider changes, model deprecation, pricing or quota shifts,
   route outages, changing task mix — so a policy learned on stale conditions does not silently
   degrade a task?
10. What staleness windows and expiry apply to learned parameters, and how is a policy invalidated
    when its evidence ages out or its route changes?
11. How is a learned policy kept from corrupting D-024 continuity — for example re-routing an
    already-authorized task, changing its context shape mid-flight, or overfitting one project's
    history — and how is a policy rolled back without losing canonical evidence?
12. How are per-project, per-goal and per-user data kept from leaking into a shared policy, and how
    is cross-project learning prevented or explicitly bounded by privacy scope?

### Guardrails, floors and reward hacking

13. What hard floors and guardrails bound adaptation — correctness and acceptance floors, hard
    cost/latency/quota ceilings, privacy and egress limits, authority invariants, safety floors —
    and how are they enforced so no reward can trade against them?
14. How is reward hacking prevented or detected: gaming first-review acceptance, suppressing
    hard cases, routing to a lenient judge, shrinking tasks to inflate completion, hiding rework, or
    optimizing a proxy that diverges from the real objective?
15. What methods keep the reward honest — held-out and adversarial evaluation, human spot checks,
    distribution-shift detection, counterfactual/logged-policy evaluation, outcome auditing — and
    what is the falsifier for each?
16. How is an adapted policy made observable and reversible, with its provenance, evidence,
    uncertainty and rollback recorded, so an operator can answer why a routing decision was made
    zero-token?

### Optionality and decisive falsifiers

17. What must "optional and off by default" mean concretely — no measurement call, no model call,
    no policy write, no egress when disabled — and what is the inertness predicate?
18. What is the decisive **no-benefit** falsifier: a preregistered comparison where the adapted
    policy is not measurably better than the conservative static policy on the accepted objective,
    and what non-inferiority margin decides it?
19. What is the decisive **regression** falsifier: a case where adaptation increases cost, latency,
    quota burn, rework or false acceptance, or reduces correctness, continuity or
    recoverability — and what measured threshold reverses the preference?
20. What provider-free fixtures must accept or reject: an offline-policy promotion, an exploration
    cap, a floor-violation refusal, a reward-hacking tripwire, a non-stationarity invalidation, a
    rollback, a privacy-isolation probe and a disabled-path inertness soak — and what is the exact
    pass/fail predicate for each?
21. How do the fixtures prove that no learned parameter widens authority or approves an effect,
    that a disabled learner is inert, that a Stop interrupts and reverts an experiment, and that a
    policy change cannot corrupt canonical evidence or continuity — using synthetic outcomes only,
    with no provider call?
22. How is each result classified as source-documented, locally observed, inferred or `unknown`,
    and what does the suite not establish — for example no measured improvement, no guarantee
    against reward hacking, no coverage of every provider's behavior, no route qualification and no
    entitlement?

## Deliverable

An adaptive-optimization and outcome-learning design candidate containing: a scope section naming
which routing, prompt, tool and compaction policies may adapt and which stay fixed, and stating
that policy never confers authority; an evidence section defining the measured outcome signals with
provenance-qualified counters; an offline-versus-online section covering exploration cost, caps and
the promotion path; a non-stationarity and continuity section covering staleness, invalidation,
rollback and privacy scoping; a guardrails-and-anti-reward-hacking section with hard floors,
tripwires and honest-reward methods; an optionality section fixing off-by-default inertness; and a
provider-free fixture suite for promotion, exploration caps, floor refusal, reward-hacking
tripwires, non-stationarity invalidation, rollback, privacy isolation and disabled-path inertness.
Each recommendation names a competing option, a decisive falsifier (including no-benefit and
regression) and what it does not prove. No language, store, framework, model, routing algorithm,
bandit, optimizer or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, model, routing algorithm, bandit,
  optimizer, tuner or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that a learned policy confers authority, approves an effect or improves quality,
  cost or quota where no preregistered measurement and independent result exist.
- No vendor-sabotage narrative; every cost, quality and routing comparison is a measured fact with
  provenance and uncertainty (D-031).
- No online exploration on live, irreversible or human-gated actions; no spend, deployment or
  publication by a learner.
- No provider, model, credential or account call; no live experiment run; every fixture is
  synthetic and provider-free.
- No claim of reward-hacking immunity, exploration-bound or non-stationarity guarantee without
  measurement; those cells stay `unknown`.
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive.
- No reopening of D-018, D-019, D-022, D-024 or D-031.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The scope section names the adapting policies (route/provider/model, prompt/context, tool/harness,
  compaction/cache, fan-out/retry) and the fixed ones, and states that adapted policy can never
  widen authority, approve an effect, alter privacy scope or change an acceptance gate.
- The evidence section defines provenance-qualified outcome signals and keeps `unknown` distinct
  from zero.
- The offline-versus-online section defines both modes with a competing option, exploration caps
  that exclude live/irreversible actions, and a promotion path that requires independent or human
  approval.
- The non-stationarity and continuity section defines staleness windows, invalidation, rollback
  without evidence loss, and privacy scoping that prevents cross-project leakage into a shared
  policy.
- The guardrails section names hard floors (correctness/acceptance, cost/latency/quota ceilings,
  privacy/egress, authority invariants, safety) that no reward may trade against, and specifies
  reward-hacking detection and honest-reward methods.
- The optionality section fixes an off-by-default inertness predicate with zero call, zero write
  and zero egress when disabled.
- The candidate gives decisive no-benefit and regression falsifiers with a non-inferiority margin
  and reversal threshold, and the provider-free fixture suite specifies predicates for promotion,
  exploration caps, floor refusal, reward-hacking tripwires, non-stationarity invalidation,
  rollback, privacy isolation and disabled-path inertness, with no provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, model, routing algorithm, bandit, optimizer or vendor is selected
  and no route is qualified.
- The candidate explicitly states what it does not establish: no measured improvement, no
  reward-hacking or non-stationarity guarantee, no route qualification and no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.
