---
title: DS-03 — Risk-scaled verifier independence
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-03 — Risk-scaled verifier independence

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

- **Focus.** This lane defines the verifier-independence vector, risk tiers, documented downgrade and release-blocking rules, so the verification contract can be frozen. It is research lane R5 of the Recursion v3 agenda.
- **Independence vector.** Independence is a vector, not a model label. Its dimensions are actor, workspace/state, evidence acquisition, implementation authorship, model family, provider, account/capacity pool, host/failure domain, and evaluator/oracle.
- **Risk tiers `V0`–`V3`.** `V0-mechanical`: deterministic gate re-execution; a model adds no authority. `V1-routine-reversible`: a clean separate verifier actor/context with exact gate rerun. `V2-sensitive`: V1 plus an independent failure domain (different model family/provider, deterministic specialist/oracle or human review) and an adversarial fault gate. `V3-constitutional-release`: deterministic gates, a separate verifier, a required independent failure domain and authenticated Owner approval.
- **Accepted direction.** `OR-006` ratifies risk-scaled independence: routine work may use a documented downgrade, while releases, security-sensitive work, control-plane changes and irreversible external effects block unless Lucas explicitly approves an exception. Missing or weaker verification is recorded and can never become a pass.
- **Canonical vector and receipt.** `CA-V3-005` and `CA-V3-006` are the clauses of the future constitutional amendment that define the one canonical independence vector and the single-use `VerifierDowngradeReceipt`. This research must not define a second vector.
- **Downgrade semantics.** A risk-approved exception yields only `downgraded-pass`/`terminal-verified-downgraded` for its exact candidate; it may never be displayed, queried or published as `pass`, full verification or cross-family review. A missing verifier is `blocked/missing`; a failed verifier is `fail`.
- **Same-family limits.** Sol/Luna/Terra are the same model family, so same-family review is useful actor/context separation but is never reported as cross-family independence.
- **`OR-020`.** The Owner authorization for the docs-only amendment that carries these classes; it remains non-operative until applied.
- **Boundary.** This lane may not select a product verifier, enable a route or spend quota; it produces evidence and options only.

## Purpose

This research informs the verifier-independence vector, risk tiers, documented downgrade and release-blocking rules, so the verification contract can be frozen. It is blocking because `OR-006` ratifies risk-scaled independence whose exact dimensions and evidence are unresolved, and because a false green gate is the system's worst failure. Missing or weaker verification must never become a pass.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane may not select a product verifier, enable a route, or spend quota; it produces evidence and options only. The canonical independence vector and downgrade receipt are defined by `CA-V3-005`/`CA-V3-006` in the future constitutional amendment, and this research must not define a second vector.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. Which independence dimensions — separate task, context, session, model, family, provider, host/failure domain, and oracle — measurably improve defect detection for each risk class?
2. How do risk tiers `V0`–`V3` map to deterministic gates, same-family separation, cross-family review, cross-provider review and independent execution environment?
3. What documented downgrade shape satisfies routine reversible work without ever being reported as full independence?
4. What exactly must block for release, security-sensitive, control-plane and irreversible work when the required verifier is unavailable, and what must an Owner exception bind to be valid?
5. How is a blind, preregistered matrix designed so the implementer cannot persuade the verifier or leak candidate identity?
6. What fallback applies when independent routes are unavailable — human review, deterministic specialist/oracle, or cross-host rerun — and what are each one's limits?
7. How is verifier collision detected and refused when implementer and verifier share family, provider, account/pool, host, session or evidence channel?
8. What public software-assurance, reproducible-build, safety-case and multi-model evaluation evidence supports or contradicts each independence dimension?
9. Which metrics (first-review acceptance, escaped defects, disagreement rate, false-green gates) can distinguish dimensions without a hidden scalar score?
10. What evidence hierarchy prevents a stronger-model claim from replacing an exact deterministic gate execution?
11. What single-use receipt bindings, expiry and consume semantics prevent a downgrade exception from being reused or relabeled as `pass`?
12. What competing option (single universal strong verifier) fails, and by what decisive falsifier in a preregistered sample?

## Deliverable

- A source-pinned claim table classifying each independence dimension by risk class, confidence and expiry.
- A risk-tier table with minimum assurance, downgrade rule and blocking rule for each class.
- A preregistered blind matrix with exact candidates, treatments, metrics and deterministic gates.
- A recommendation tied to a competing option and a decisive falsifier, plus open Owner questions.

## Non-goals

- Do not issue, consume or simulate a downgrade receipt or Owner exception.
- Do not reopen `OR-006`, `OR-020` or the `CA-V3-005`/`CA-V3-006` vector.
- Do not claim any missing verification as a pass or a full independence result.
- Do not select a product verifier, route, provider or model, or spend any quota.
- Do not edit constitution, auth, config or acceptance state.
- Do not include private project identity, transcripts or local paths.

## Completion gate

- Every independence claim is pinned to a primary source or explicitly marked unverified.
- The tier table covers all four classes with downgrade and blocking rules and no silent gap.
- Every recommendation carries a competing option and a decisive falsifier.
- Missing or downgraded verification is never described as `pass` or full independence.
- `OR-006`/`OR-020` are neither reopened nor promoted, and no second vector is defined.
- No protected path is edited and no runtime/provider/auth/cron/PAUSE/spending effect occurs.
- The deliverable passes a privacy and secret scan; Owner questions are listed separately.
