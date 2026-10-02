---
title: R-W — Harness evaluation and benchmark science
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-W — Harness evaluation and benchmark science

This is an evaluation-methodology handoff for accepted Owner decisions D-018, D-019, D-022,
D-024 and D-031, with the gap register in [GAPS.md](../../research-lane/GAPS.md). It builds
directly on [R-D](../dot-research-20261002/R-D-quota-efficiency-measurement.md), the
quota-efficiency measurement handoff, and on
[R-O](R-O-performance-and-configurability-engineering.md), the backend-performance handoff, and
must extend rather than restate them: R-D specifies quota and lock-in measurement and R-O
specifies the backend matrix, while R-W designs the **evaluation science** — task suites,
acceptance gates, regression detection, false-green control, statistical rigor, preregistration,
held-out generalization, endpoint selection and comparability — that judges a harness
end-to-end. It consumes the unmeasured findings DS-10 (performance/benchmark), DS-11
(routing/delegation endpoints) and R-D and must not invent benchmarks those lanes did not record.

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

- The object of study is **how Recursion decides whether the harness is good**. A harness is not
  a model; it is the orchestration around a model, so its evaluation must use task suites with
  objective acceptance gates, must detect regressions and false greens, must be statistically
  honest and preregistered, must test held-out generalization, and must report cost, quality and
  human-effort endpoints together rather than a single score.
- D-024 makes **productive continuity** the headline measurable differentiator and adopts six
  demonstration journeys as release acceptance scenarios. Evaluation therefore centers on
  continuity endpoints — survival of harness change, compaction, source fork and lost machine
  with authority, evidence and honest accounting preserved — not on feature counts, and must beat
  strong baselines in verified outcomes and human effort.
- D-018 makes Recursion a first-class native harness *and* a unifying wrapper whose purpose is to
  remove lock-in and cut quota/usage burn. Evaluation must therefore compare Recursion against
  driving each harness directly, on the same tasks, and must be able to attribute any difference
  to the harness rather than to an unfair model, prompt or budget advantage.
- D-019 ships every capability as an **opt-in plugin or profile** with no default spend. The
  benchmark matrix must therefore be run with capabilities disabled and enabled separately, and
  the disabled baseline must be shown to spend nothing; a capability that cannot be toggled
  without changing the task is not a clean treatment.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. Evaluation must define how interruption, checkpoint and drain are
  exercised as controlled treatments and how a Stop is distinguished from a crash in the
  endpoint accounting.
- D-031 forbids a "vendors sabotage quota" claim and requires savings to be claimed only when
  measured per workload. Evaluation must never infer vendor intent from cost or retry data, and
  must report a null or negative result as a result.
- Authority is not origin-based; similarly, a benchmark result carries no authority until it is
  independently rerun under an accepted protocol. An implementer's own PASS is never acceptance;
  evaluation results are subject to independent verification and to deliberate false-green
  control.
- The recorded evidence this lane must preserve: DS-10 treats Option 2's benefit as unverified
  and the benchmark manifest as the top unresolved input; DS-11 proposes task-specific route
  suites with first-review acceptance and false-green rate as primary endpoints, with no local
  measurement; DS-12 records the context/compaction suite as unrun; DS-26 records that counters
  cannot drive budgets until telemetry adapters are runtime-qualified. GAPS G-20, G-22 and G-27
  record these as unrun `experiment` gaps. No benchmark result exists for Recursion, and no
  benchmark may be invented here.
- Already accepted direction this lane must respect: the canonical writer defines the
  authoritative event order; counters keep `unknown` distinct from zero; evidence classes are not
  collapsed; every recommendation carries a competing option, a decisive falsifier and an
  explicit non-proof; and review throughput, not token generation, is the binding constraint.
- Prior comparison coverage to extend, not reinvent: the public evaluation practice in
  peer-reviewed software-engineering and ML systems work, preregistration and registered-report
  practice, non-inferiority and equivalence testing, multiple-comparison control, test-flakiness
  and mutation-testing literature, and the documented public benchmark suites of upstream
  harnesses. Named external suites are cited from public documentation, not adopted or endorsed.
- Evidence status: no task suite, acceptance gate, regression harness, false-green control,
  preregistration or held-out evaluation has been executed by Recursion for this lane. Every
  endpoint, threshold, power figure and generalization claim below is to be established from
  public methodological source and a preregistered protocol, or marked `unknown`.

## Purpose

Produce the decision-ready **harness evaluation and benchmark-science design candidate** for
Recursion. The lane specifies task-suite construction and sampling; objective acceptance gates
and grader independence; regression detection and drift monitoring; false-green control
including mutants and negative controls; statistical rigor, preregistration, power, effect sizes
and multiple-comparison control; held-out and out-of-distribution generalization; a multi-
endpoint reporting standard (verified quality, quota/usage cost, wall time, and human effort);
and comparability, provenance and publication rules. It ties every endpoint to DS-10, DS-11,
DS-12, DS-25, DS-26 and R-D rather than inventing a benchmark, and it states the falsifier for
each methodological claim. It does not run a benchmark, does not select a language, store,
framework, statistical package or vendor, does not qualify any route, and executes no provider
call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, statistical package, benchmark suite or
vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024 or D-031. No
provider, model or account call is made; no benchmark or evaluation is executed; no credential
or account is touched. Do not invent a benchmark, corpus, difficulty mix, threshold or result
that DS-10, DS-11, DS-12, DS-25, DS-26 or R-D did not record; those lanes leave every cell
unmeasured and the finding is `unknown`. Do not claim a measured quality, cost or human-effort
advantage; it is a hypothesis with a preregistered falsifier. Do not attribute cost or retry
behavior to vendor intent (D-031). Treat named external benchmark suites as prior art cited from
public documentation, not as selected components.

## Inputs to read

None from this repository: the rescope, the continuity endpoints, the honest-counter contract and
the unmeasured performance/routing/context findings are summarized in `## Baked context` above,
and no repository, connector or private-source access is assumed. The session must, however,
retrieve the public methodological and product documentation it cites — the SWE-bench and
similar public coding-benchmark papers and dataset cards, the ML-reproducibility and model-
evaluation literature, preregistration and registered-report guidance, non-inferiority and
equivalence-testing references, multiple-comparison and sequential-analysis references, test-
flakiness and mutation-testing literature, and the public evaluation documentation of the
upstream harnesses named in the comparison — and pin each claim to a URL and retrieval date.

## Research questions

### Task suites and acceptance gates

1. How are task suites constructed so they measure the harness rather than a model: what task
   families, difficulty strata, repository/source conditions and failure modes, and how is the
   suite sampled and sized to be representative without becoming an unmaintainable corpus?
2. What is an **objective acceptance gate** for a task — a machine-checkable pass/fail predicate
   that is independent of the implementation under test — and how are gates validated so a task
   cannot be passed by a proxy (formatting, tautology, leaked answer) rather than by the intended
   behavior?
3. How are task gates made **provider-neutral and route-neutral** so the same suite judges the
   native harness and a delegated upstream harness without encoding one runtime's assumptions?
4. How does the suite exercise the D-024 continuity endpoints — harness change, compaction,
   source fork and lost machine — as first-class tasks rather than as incidental scenarios, and
   what gate proves authority, evidence and accounting survived?

### Regression detection and false-green control

5. What regression-detection design detects a quality, latency or cost regression reliably, with
   a defined baseline, a defined tolerance, and a plan for benign drift versus real regression?
6. What **false-green control** is required: negative controls and known-bad candidates that must
   fail, mutation or perturbation of the harness, grader-independence checks, and a fake-pass
   suite that would expose a grader that accepts anything?
7. How are the spec-level false-green rate and the first-review acceptance rate made primary
   endpoints (DS-11) without conflating them with the runner's internal self-report?
8. How is **flakiness** measured and bounded — repeated runs, variance decomposition, quarantine
   of unstable tasks, and a rule for when a flaky gate invalidates a result — so a lucky pass is
   not recorded as progress?

### Statistical rigor, preregistration and generalization

9. What preregistration is required before a confirmatory run: hypotheses, primary and secondary
   endpoints, task suite and version, treatments and controls, stopping rule, analysis plan,
   exclusion rules, and the decision the result will inform — recorded before data collection?
10. What power, sample-size and effect-size policy is required so a null result is distinguishable
    from an underpowered one, and what uncertainty is reported (intervals or credible intervals,
    not point estimates alone)?
11. How are multiple comparisons controlled across task classes, routes and endpoints, and how is
    a sequential or adaptive analysis handled without inflating the false-positive rate?
12. How are **held-out** and out-of-distribution task families reserved so a harness tuned on the
    development suite is judged on tasks it has not seen, and what is the falsifier for a claim of
    generalization?
13. How are negative and null results, and experiments that were abandoned, recorded and
    published so the evaluation record is not survivorship-biased?

### Endpoints, comparability and publication

14. What multi-endpoint reporting standard is required — verified task quality, quota/usage cost,
    wall time/latency, reliability, and **human effort** such as owner-review minutes and
    corrections — and why must no single scalar stand in for all of them (DS-10, DS-11, R-D)?
15. How is a comparison made fair and comparable: matched model, matched budget, matched context
    policy, matched hardware and platform profile, identical tasks, and an accounting that counts
    retries, compactions, wasted work and human corrections exactly once?
16. How is human effort measured honestly and comparably — review minutes, number of corrections,
    rework, and acceptance latency — and what is the cost of measuring it?
17. How does the evaluation demonstrate the D-018 anti-lock-in claim: that a goal can be driven
    through more than one harness/route without holding ungranted credentials and that measured
    quota/usage burden falls versus driving each harness directly — or the public claim is
    withdrawn (D-031)?
18. What provenance and publication rules are required: pinned suite version, pinned harness and
    adapter revisions, raw data retention within privacy limits, an explicit statement of what the
    result does not prove, and a rule that a benchmark result carries no authority until
    independently rerun under the accepted protocol?

### Provider-free and non-provider evaluation

19. Which evaluation layers can run provider-free — deterministic kernel, routing/admission logic,
    replay, containment, regression detection, grader validation, mutation and false-green
    control — and which inherently require live provider spend and are therefore human-gated?
20. How does the cheap provider-free layer gate promotion to a live, spent, preregistered run, so
    that expensive confirmatory evaluation is only reached by candidates that passed the
    deterministic gates?
21. What does a harness benchmark explicitly **not** prove: no universal superiority, no claim
    beyond the suite and version, no model-quality claim, no vendor-intent claim, and no
    generalization without a held-out result?

## Deliverable

A harness evaluation and benchmark-science design candidate containing: a task-suite and
acceptance-gate section defining task families, sampling, objective and grader-independent gates,
and continuity tasks; a regression and false-green section defining detection, negative controls,
mutation/perturbation and flakiness bounds; a statistical-rigor section defining preregistration,
power, effect sizes, uncertainty, multiple-comparison control and held-out/out-of-distribution
reservation; an endpoint and comparability section defining multi-endpoint reporting (verified
quality, quota/usage cost, wall time, human effort), matched-treatment fairness and single-count
accounting; a provenance and publication section defining pinning, raw-data retention, non-proof
statements and independent rerun; and a provider-free gate that must pass before any spent
confirmatory run. Every endpoint ties to DS-10, DS-11, DS-12, DS-25, DS-26 or R-D, and no
benchmark, threshold or result is invented. Each recommendation names a competing option, a
decisive falsifier and what it does not prove. No language, store, framework, statistical
package, benchmark suite or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, statistical package,
  benchmark suite or vendor.
- No execution of a benchmark, evaluation, model run or provider call; no route qualification, no
  account or subscription entitlement claim, no eligibility finding, and no spend.
- No invented benchmark, corpus, difficulty mix, sample size, power figure, threshold or result;
  anything DS-10, DS-11, DS-12, DS-25, DS-26 or R-D left unmeasured remains `unknown`.
- No claim of measured quality, cost or human-effort superiority, and no "vendors sabotage quota"
  claim; savings are claimed only when measured per workload (D-031).
- No single scalar score presented as the evaluation verdict; cost, quality and human effort are
  reported together with uncertainty.
- No benchmark result treated as authoritative without independent rerun under the accepted
  protocol; an implementer's own PASS is never acceptance.
- No provider, model, credential or account call; the provider-free layer is the only layer
  executed here.
- No new executive tier, no standing autonomous executive and no self-promoting evaluation agent.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no reopening of the accepted findings
  in DS-10, DS-11, DS-12, DS-25, DS-26 or R-D.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The task-suite section defines task families, difficulty strata, sampling and sizing, an
  objective grader-independent acceptance gate, a check that a task cannot be passed by a proxy,
  and first-class continuity tasks for harness change, compaction, source fork and lost machine.
- The regression and false-green section defines detection with a baseline and tolerance,
  negative controls and known-bad candidates that must fail, grader-independence and fake-pass
  checks, flakiness measurement and quarantine, and the spec-level false-green and first-review
  acceptance primary endpoints of DS-11.
- The statistical-rigor section defines preregistration contents, power and sample-size policy,
  effect sizes and uncertainty reporting, multiple-comparison control, sequential/adaptive
  handling, held-out and out-of-distribution reservation, and null/abandoned-result retention.
- The endpoint section defines verified quality, quota/usage cost, wall time and human effort as
  separate endpoints with matched-treatment fairness and single-count accounting of retries,
  compactions, wasted work and human corrections.
- The comparability and publication section defines pinned suite/harness/adapter versions, raw-
  data retention within privacy limits, explicit non-proof statements, and the rule that a result
  carries no authority until independently rerun.
- The provider-free layer is defined and gates any live, spent, preregistered confirmatory run;
  every live run is recorded as human-gated.
- Every endpoint ties to a recorded DS-nn or R-D finding, and no benchmark, threshold or result
  is invented; unmeasured cells remain `unknown`, never zero.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, store, framework, statistical package, benchmark suite or vendor is
  selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured advantage, no universal
  superiority, no claim beyond the suite and version, no model-quality claim, no generalization
  without a held-out result and no vendor-intent claim.
- Protected paths are untouched; privacy and secret scan are clean.
