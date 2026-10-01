---
title: DS-34 — Decision journaling and calibration
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not stop at a plan, outline, scope sheet, or clarification request — execute the research now and return the final report.

# DS-34 — Decision journaling and calibration

This is a self-contained Deep Research handoff. Supplying this document is the invocation; it makes no repository or provider call on its own. Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. It is a public/synthetic research lane and includes no private decision content.

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

- Recursion v3 is a provider-neutral agent platform whose operation is tracked through durable, reviewable decisions. The owner is final authority; the operative constitution defines decision precedence and requires that superseded and amended decisions preserve their original reasoning.
- Existing decision log: the repository keeps a D-entry decision log with, by rule, every decision carrying a falsifier, and a monthly first-of-month review cadence. D-017 is one recorded D-entry (the git-as-transport/`state/` decision). Existing D-entries are history and must not be rewritten, renumbered or edited. A candidate schema must reconcile with the D-entry convention rather than propose a parallel log, and must state what it does not duplicate.
- The problem: individual project decisions should be scored against their predicted outcomes rather than reconstructed by hindsight, so forecasts must be falsifiable and actually reviewed. The morning-brief and kill-criteria disciplines depend on criteria written before outcomes are observed. A machine-checkable condition should flag a record that is missing a falsifier or is past its review date, without a model call.
- Decision scope and authority: the decision log records operating decisions; the decision register records accepted Owner directions (OR-xxx). A research session may propose reconciliation text but never edits the constitution or the logs, and never promotes a proposal into an Owner decision.
- Calibration evidence to apply: the forecasting and calibration literature (Tetlock and successors) establishes measurable skill, the difference between domain expertise and general forecasting skill, the effect of continuous versus one-shot feedback, and the limits of small samples. For a low-volume individual log, appropriate accuracy, resolution and calibration measures must be chosen and the misleading-at-small-sample ones named.
- Journal and reference-class content: a decision-journal entry is reviewable when it records decision, options, choice, rationale, expected outcome, falsifier and review trigger. Reference-class forecasting and base rates supply an outside view but are hard to construct at small scale; base rates must be recorded, updated and reconciled with inside-view detail as local history accumulates without overfitting to a handful of cases.
- Failure modes to mitigate: hindsight bias, outcome bias, motivated reconstruction, vague success criteria, journals written once and never reviewed, and survivorship/selection/small-sample effects that make a lucky call look like skill. Each needs an entry-time or review-time rule.
- Cadence and state transitions: candidate review triggers are time-based, event-based (a falsifier fired, a project closed, a threshold crossed) or a combination. A decision record may carry states such as open, held, failed, unclear or superseded, and a fired falsifier and a superseded/amended decision must preserve the original reasoning without rewriting history.
- Research constraints: this is a public/synthetic lane and includes no private decision content, transcripts, local paths or credentials. It performs no runtime, tool, journaling-application or automation implementation and selects no language, store, format or tool as a product decision. It must not rewrite existing D-entries, reopen accepted Owner decisions or the anchor scope, make provider/model calls or a model-graded review, present an invented base rate as a measured local value, or claim that a low-volume log yields statistically strong calibration.

## Purpose

Decide a decision-log schema and a review cadence that make forecasts falsifiable and actually reviewed, so that individual project decisions can be scored against their predicted outcomes instead of reconstructed by hindsight. This is blocking because the repository already keeps a D-entry decision log with falsifiers and a monthly review cadence, and because the morning-brief and kill-criteria discipline depends on criteria written before outcomes. The research must reconcile with the existing D-entry convention rather than propose a parallel log, and must connect to the accepted research scope.

## Authority and boundaries

The shared authority constraints are in `## Baked context`. Preserve the current constitution; write proposed reconciliation, never edit it. Public or synthetic briefs only — never private decision content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. Do not reopen accepted Owner decisions or anchor scope, and do not select a tool, store or format as a product decision. Existing D-entries are history and are not to be rewritten.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Calibration and forecasting evidence

1. What does the forecasting and calibration literature (Tetlock and successors) establish about measurable skill, and under what conditions does it transfer from a forecasting tournament to individual project decisions?
2. What accuracy, resolution and calibration measures are appropriate for a low-volume individual log, and which are misleading at small sample sizes?
3. How does continuous versus one-shot feedback change calibration, and what does the record show about how quickly individual judgment improves?
4. What do the studies report about domain expertise versus general forecasting skill for technical and project decisions?

### Decision-journal formats and reviewed fields

5. Which decision-journal formats are documented in practice, and which fields are actually revisited versus written once and abandoned?
6. What is the minimum field set that makes a decision reviewable: decision, options, choice, rationale, expected outcome, falsifier and review trigger?
7. How do you record a decision whose outcome is one of several gradations rather than a binary, and where do journals fail once they become a compliance ritual?

### Base rates and reference-class forecasting

8. How is a reference class chosen for a personal project decision, and what does the literature say about the failure to find an appropriate class and the outside-view correction?
9. What base rates are available or constructible for recurring decisions in a small operation (project length, rework, abandonment, review debt, estimate error)?
10. How should base rates be recorded, updated and reconciled with inside-view detail as local history accumulates, without overfitting to a handful of cases?

### Failure modes and biases

11. How are hindsight bias, outcome bias and motivated reconstruction detected and mitigated in a log that is reviewed after the outcome is known?
12. What makes success criteria vague, and how is vagueness caught at entry time rather than at review time?
13. What does the record show about journals written but never reviewed, and what trigger or cadence reliably drives the review?
14. How are survivorship, selection and small-sample effects kept from making a lucky call look like skill?

### Schema and review cadence

15. What decision-log schema should be used, with required versus optional fields, and how does it map onto the existing D-entry template?
16. What review cadence and trigger conditions are evidence-backed: time-based, event-based (falsifier fired, project closed, threshold crossed), or a combination?
17. What state transitions should a decision record carry (open, held, failed, unclear, superseded) and how is a fired falsifier treated?
18. How are superseded and amended decisions preserved with the original reasoning, as the operative constitution requires, without rewriting history?

### Reconciliation with Recursion's conventions

19. How does a candidate schema reconcile with the existing D-entry log, the monthly first-of-month review and the "every decision gets a falsifier" rule, and what does it add without duplicating?
20. How should the morning brief and kill-criteria discipline feed the decision log so predicted outcomes are recorded before the outcome is observed, and what machine-checkable condition flags a record missing a falsifier or past its review date without a model call?

## Deliverable

- A source-pinned claim table (claim, source, version/date, classification as fact/inference/hypothesis/proposal, confidence, expiry or falsifier trigger).
- A decision-log schema with required and optional fields, shown as a reconciliation with the existing D-entry template.
- A review cadence with specific trigger conditions, distinguishing time-based from event-based triggers and stating the evidence for each.
- A base-rate and reference-class recording approach with the small-sample caveat stated.
- One recommendation tied to a named competing option and a decisive falsifier, plus open Owner questions.

## Non-goals

- No runtime, tool, journaling application or automation implementation.
- No language, store, format or tool selection as a product decision.
- No rewriting, renumbering or editing of existing D-entry decisions.
- No reopening accepted Owner decisions or anchor scope.
- No private decision content, transcripts, local paths or credentials in any public packet.
- No provider or model calls, and no model-graded review performed.
- No invented base rate presented as a measured local value.
- No claim that a low-volume individual log yields statistically strong calibration.

## Completion gate

- Every calibration, bias and base-rate claim is pinned to a primary source with version or retrieval date, or marked unverified.
- The schema reconciles with the existing D-entry convention and states what it does not duplicate.
- Every required field has a stated reason it is reviewed later, not merely recorded.
- The review cadence names concrete trigger conditions and their evidence.
- Hindsight-bias and vague-criteria mitigations are stated as concrete entry-time or review-time rules.
- Small-sample limits are stated plainly and no calibration strength is overstated.
- Every recommendation names a competing option and a decisive falsifier.
- No existing D-entry is edited and no protected path is modified.
- Open Owner questions are listed separately from research findings.
