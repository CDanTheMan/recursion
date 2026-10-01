---
title: DS-08 — Private canary methodology
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research and do not request further approval.

# DS-08 — Private canary methodology

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

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

- **Focus.** This lane defines what the first private canary can prove without leaking its identity or letting one successful run substitute for fault coverage. It is research lane R10 of the Recursion v3 agenda.
- **`CANARY-01`.** The first private canary, referenced by alias only. Its real project identity, path, content, hash and transcript must never appear in tracked or public artifacts.
- **Ratified first task.** `OR-010` fixes the first task as test-only characterization of one stable, deterministic, non-safety-critical business rule, with writes limited to tests and fixtures, private-approved processing, an independent clean rerun, and one local candidate commit. The canary is not authorized to run by that ruling, and it must not run during this research campaign.
- **Write boundary.** Test/fixture-only and machine-checkable. No production writes; no publication, push, merge or deployment; no provider call, so route eligibility is reasoned rather than exercised.
- **Independent clean rerun.** Clean checkout, fresh state, frozen input and deterministic expected output.
- **Baseline and substitution.** A baseline comparison must distinguish real verification from a tautological or overfit test, and one successful canary must not substitute for fault coverage or broader conformance evidence.
- **Failure-injection fixtures.** Malformed input, mismatch, crash, missing dependency and stale state.
- **Disclosure and stop conditions.** Stop on privacy or secret exposure, protected-path contact, ambiguity or an unverified claim. Disclosure rules set what may be shared, with whom, and at what classification.
- **Routes and boundary.** Private-approved routes are eligible and approval binds without recording private identifiers. No new route, model or auth selection is made here.

## Purpose

Define what `CANARY-01` can prove without leaking its identity or letting one successful run substitute for fault coverage. Agenda lane R10 blocks the first private characterization of a stable deterministic non-safety-critical business rule until its alias-only reference, test/fixture write boundary, private-approved route, independent clean rerun, failure injection and stop conditions are specified. The canary must not begin during this research campaign.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. The canary is referenced by alias only; never record its real identity, path, content or digest in tracked or public artifacts. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This campaign authorizes no canary execution, no private route call and no candidate commit.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. How is `CANARY-01` referenced by alias only, with no real project identity, path, content, hash or transcript in tracked docs?
2. What can one canary prove about the migration and verification pipeline, and what can it not prove?
3. How is one stable deterministic non-safety-critical business rule selected and characterized without touching production code?
4. What test/fixture-only write boundary is machine-checkable, and which paths must be refused?
5. Which private-approved routes are eligible, and how is route approval bound without recording private identifiers?
6. What defines an independent clean rerun: clean checkout, fresh state, frozen input and deterministic expected output?
7. What does "one local candidate commit" permit, and how does it avoid publication, push or merge?
8. Which failure-injection fixtures (malformed input, mismatch, crash, missing dependency, stale state) must the canary survive?
9. What baseline comparison distinguishes real verification from a tautological or overfit test?
10. What disclosure rules govern what may be shared, with whom, and at what classification?
11. What stop conditions abort the canary: privacy, secret exposure, protected-path contact, ambiguity or an unverified claim?
12. How does a single successful canary avoid substituting for fault coverage or broader conformance evidence?
13. What durable proof demonstrates the canary did not begin during this research campaign?

## Deliverable

A source-pinned report with: a claim table (claim, source, version/date, classification, confidence, expiry trigger); an alias-only runbook shape; the exact machine-checkable write boundary; private-route eligibility rules; failure-injection, baseline, disclosure and stop conditions; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions.

## Non-goals

- The canary must not run during this research campaign.
- No real project identity, path, content, transcript or digest in tracked or public docs.
- No production writes; tests and fixtures only.
- No publication, push, merge or deployment.
- No provider call; route eligibility is reasoned, not exercised.
- No new route, model or auth selection.
- No claim of conformance, release readiness or migration completion from one canary.
- No reopening of the ratified first-canary scope.

## Completion gate

- Alias-only reference is verified; no real identity or content appears in tracked output.
- The write boundary is machine-checkable and limited to tests and fixtures.
- Independent clean rerun and baseline comparison are specified.
- Failure injection, disclosure and stop conditions are listed and falsifiable.
- The report states the canary did not start and no candidate commit was created here.
- Private-approved route eligibility is stated without recording private identifiers.
- What the canary proves is separated from what it cannot prove.
- Protected paths are untouched; privacy and secret scan are clean.
