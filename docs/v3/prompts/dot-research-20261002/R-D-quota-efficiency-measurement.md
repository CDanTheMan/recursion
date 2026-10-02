---
title: R-D — Falsifiable quota, usage and lock-in measurement
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-D — Falsifiable quota, usage and lock-in measurement

This is a rescope handoff for accepted Owner decisions D-018 and D-024, and the gap register in
[GAPS.md](../../research-lane/GAPS.md).

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Hermes is the executive control plane. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

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

- D-018 reframes Recursion as both a native harness and a unifying wrapper whose purpose is to
  remove lock-in and cut quota/usage burn, shipped community-based and open-source. Its
  consequence records that the claim that vendors deliberately unoptimize quota is a
  **hypothesis requiring a falsifiable experiment**, never a fact. Its falsifier is that honest
  measurement shows Recursion cannot reduce quota/usage burden.
- D-024 makes productive continuity the headline measurable differentiator and requires it to
  beat strong baselines in verified outcomes and human effort, so evaluation focuses on
  continuity endpoints rather than feature counts.
- Prior context research distinguishes provider prompt/KV caches, which are scoped to provider,
  model family, account, endpoint, prefix or session, from Recursion-owned evidence reuse, and
  warns that a cache hit cannot validate a grant, evidence freshness, subscription debit or
  cross-provider reuse. Published rules differ across endpoints and must not be copied between
  them.
- Prior work requires counting cache writes and reads, every compactor, refresh, retry and
  output, verification and human correction, and using `unknown` for unavailable counters. No
  numeric quota or token-saving advantage is established by prior campaigns, and no provider
  experiment has been run.
- No quota-efficiency experiment exists. The honest status of every savings claim is unmeasured,
  and the premise "vendors deliberately unoptimize quota" is untested.

## Purpose

Produce the preregistered, falsifiable experiment design that tests whether Recursion reduces
quota/usage burn and lock-in relative to using each harness directly. This is a measurement-design
lane: it defines endpoints, confounders, a preregistration template and hard floors. It does not
call any provider, spend money, consume quota, or assert the outcome. The premise that vendors
deliberately unoptimize quota is treated strictly as a hypothesis to be falsified.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT assert that vendors unoptimize quota,
and DO NOT claim any savings, cache benefit or lock-in reduction before measurement.** Do not
select a language, store, framework, metric weighting or vendor. No provider, model, network or
paid route call is authorized; no quota is consumed and no money is spent. Do not decide an Owner
question recorded in D-018 or D-024. Numerical budgets must not be invented before measurement;
unavailable counters stay `unknown`.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Measurable endpoints and accounting

1. What is the complete endpoint dictionary for quota, usage and lock-in — quota-native
   allowance (for example plan limit, remaining allowance, reset window), input/output tokens,
   cache reads and cache writes, reasoning or thinking tokens, retries, helper and small-model
   calls, compaction and summarization cost, verification cost, and human effort — and what
   denominator and unit does each carry?
2. For each endpoint, what is publicly observable versus provider-internal, and where must the
   honest value be `unknown` rather than an estimate presented as fact?
3. How are attempts that produce no usage report, interruptions and partial completions recorded
   so that unreported consumption is not counted as zero?
4. How is human effort operationalized (wall-clock, correction count, re-prompt count, reviewer
   minutes) with a denominator that does not let Recursion look cheaper by shifting work to a
   person?

### Confounders and controls

5. What are the confounders that could produce a false savings result — prompt-cache warmth and
   TTL, model and effort changes, account tier and reset timing, tool/helper configuration,
   network variability, task difficulty, repo size, session affinity, and differing hidden
   system behavior — and how is each controlled, randomized or recorded as a covariate?
6. What is the fair baseline per route: using the harness directly, with the same goal, same
   repository revision, same acceptance gate and matched model/effort, and how is "matched" made
   explicit rather than assumed?
7. What separate counterfactuals are required (cold start, warm affinity, reconstruction after
   session loss, no-future-work) so that a warm-session advantage is not reported as a general
   savings?
8. How is cross-provider and cross-route reuse distinguished from same-provider cache hits, and
   why must the two never be summed as one saving?

### Preregistration and hard floors

9. What is a preregistration template that fixes, before running: the hypothesis and its
   falsifier, the endpoint dictionary, the baseline, the randomization, the sample and stopping
   rule, the exclusion rules, the analysis, and the classification of every cell as measured,
   modelled or `unknown`?
10. What are the hard floors (authority, safety, privacy, correctness, reproducibility) that must
    be checked before any quota, cost or speed comparison, and which single failure stops the
    comparison?
11. How is the experiment made reproducible and provider-free where possible (synthetic or
    scripted inputs, frozen toolchain, immutable artifact identity) so that a rerun on a changed
    host is a new experiment rather than a silent extension?
12. What are the decisive falsifiers: what result would show Recursion does not reduce burn, and
    what result would show lock-in is not reduced, including the honest possibility of
    no-difference or worse?

## Deliverable

A report containing: the measurable-endpoint dictionary with denominators and observability; a
confounder register with controls; a matched-baseline definition per route; the required
counterfactuals; a reusable preregistration template; the hard floors and stop conditions; and
explicit decisive falsifiers, including no-difference and worse outcomes. Every proposed metric
names its denominator, its evidence class, its competing option and what it does not prove. The
premise that vendors deliberately unoptimize quota is stated only as a hypothesis with a
falsifier.

## Non-goals

- No provider, model, network, login or paid route call; no quota consumed and no money spent.
- No assertion that vendors unoptimize quota and no savings claim before measurement.
- No selection of a language, store, framework, metric weighting or vendor.
- No numeric budget invented before measurement.
- No summation of provider cache hits and Recursion-owned reuse as one saving.
- No decision of D-018 or D-024.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The endpoint dictionary names quota-native allowance, tokens, cache reads/writes, retries,
  helper/compaction cost and human effort, each with a denominator and evidence class.
- Unavailable counters are recorded as `unknown`, never zero; unreported consumption is retained.
- The confounder register controls or records cache warmth, model/effort, tier, task difficulty
  and human-effort shifting.
- The baseline is matched per route and the required counterfactuals are explicit.
- The preregistration template fixes hypothesis, falsifier, endpoints, baseline, randomization,
  sample, stopping rule, exclusions and analysis before any run.
- Hard floors are checked before any cost or speed trade-off.
- Decisive falsifiers include the no-difference and worse cases.
- The vendor-unoptimization claim appears only as a hypothesis.
- Protected paths are untouched; privacy and secret scan are clean.
