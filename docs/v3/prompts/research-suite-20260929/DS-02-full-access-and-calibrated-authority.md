---
title: DS-02 — Full Access and calibrated authority
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

**Session query — explicit invocation.** Execute research handoff `DS-02` now. This query is the explicit invocation by the Owner; the `proposed-inert` label on the brief below describes the file at rest, not this run. Do not ask which topic to research, do not request further authorization, and do not treat the attached brief as an inert document. What capability-vector contract should govern Full Access, grant administration, break-glass elevation and auditability so the grant schema can be frozen? Produce the deliverable and check every item of the completion gate.

# DS-02 — Full Access and calibrated authority

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. This file is inert until Lucas invokes it; reading or creating it launches nothing and authorizes no provider call, write, or effect.

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

- **Focus.** This lane defines the capability-vector contract behind Full Access, grant administration, break-glass elevation and auditability, so the grant schema can be frozen. It is research lane R4 of the Recursion v3 agenda.
- **Full Access.** A genuinely expansive, owner-configurable authority; the product must not advertise Full Access while silently withholding a documented capability. The implementation direction is a capability vector rather than a single ambient boolean, and each high-impact capability names its project/host/account scope, limit, acknowledgement, authentication strength, start/expiry and revocation behavior.
- **`sovereign`.** An explicit maximum preset that may include control-plane authoring, selected credential administration, provider enrollment, metered spending, publication, merge, deployment and service control when the owner grants those capabilities explicitly. `OR-005` ratifies that a maximum `sovereign` preset may explicitly include `grant-admin` and modify its own grants attributably; every mutation is a schema-checked kernel action with before/after scope, reason, authentication, expiry and durable receipt, and model text alone cannot change authority.
- **`grant-admin`.** An explicit capability, never implied by an edition or inherited ambiently, that lets a `sovereign` actor create, widen, narrow or revoke its own grants within the installation's maximum authority. `OR-014` ratifies that installing the `full` edition never implies `sovereign`.
- **Grant contract.** A grant binds issuer and subject, audience/installation, signing-key identity, parent digest, delegation depth, GoalSpec and policy versions, exact capability/effect verbs, scope, resource/spend/rate limits, not-before and expiry, revocation epoch, lease/fencing token, authentication/step-up receipt and opaque credential references. Child scope, limits, lifetime and delegation are subsets of the parent.
- **Break-glass elevation.** Attributable, bounded and recoverable privileged elevation requiring authentication strength, captured reason and automatic expiry, rather than ambient authority.
- **Audit separation.** Grant administration does not automatically include audit-retention or audit-erasure authority, and historical receipts cannot be silently rewritten or concealed. Audit-retention/erasure remains a separate unresolved Owner question.
- **Boundary.** This lane is analysis only; it grants no authority, never simulates any real authority or credential, and a model recommendation is never an Owner decision.

## Purpose

This research informs the capability-vector contract behind Full Access, grant administration, break-glass elevation and auditability, so the grant schema can be frozen. It is blocking because `OR-005` ratifies a maximum `sovereign` preset that may explicitly include `grant-admin` and modify its own grants attributably, while the operative constitution forbids self-modification until a reviewed reconciliation exists. Audit-retention and audit-erasure authority remain separate unresolved capabilities that must not be bundled into grant administration.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane is analysis only and grants no authority; a model recommendation is never an Owner decision. Audit-retention/erasure stays a separate unresolved Owner question, and the `full` edition must never be treated as implying `sovereign`.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. What is the minimal orthogonal capability vector that expresses expansive Full Access without a single ambient boolean, covering control-plane writes, credential administration, billing authority, publication, merge, deployment, service control and audit-policy change?
2. How do grant/revoke inheritance, delegation depth and non-widening subset rules compose across project, host, account, pool and endpoint scope?
3. What not-before/expiry, single-use step-up and revocation-epoch semantics prevent stale or replayed authority from admitting an effect?
4. What authentication strength, reason capture and automatic expiry make break-glass elevation attributable, bounded and recoverable rather than ambient?
5. How can explicit `grant-admin` permit a `sovereign` actor to modify its own grants while keeping model prose incapable of creating authority, with a schema-checked kernel action and before/after receipt?
6. What threat model covers confused-deputy, privilege accumulation, authority bundling, replay and stale-parent admission, and which threats are untested by signatures alone?
7. Which prior capability-OS, just-in-time-elevation, break-glass-administration and dangerous-mode designs demonstrate enforceable, auditable maximum authority, and what are their documented limits?
8. How is audit retention distinguished from grant administration, and what proof states make historical receipts non-concealable while permitting scoped raw-artifact deletion?
9. What acknowledgement and display of blast radius makes the effective capability set visible without reducing Full Access to a warning-only rubber stamp?
10. What recovery exists when a sovereign grant mutation was mistaken, given that receipts cannot be silently rewritten and states after an effect reconcile forward?
11. What deterministic test proves that installing `full` never enables maximum `sovereign`, and that a child cannot widen parent scope, limits, lifetime or delegation?
12. Which competing option — a confirmed single boolean or a preset-by-edition — fails, and by what decisive falsifier?

## Deliverable

- A source-pinned capability/grant matrix with classification, confidence and expiry for each high-impact verb.
- A threat model with per-threat falsifiers and the option tradeoffs for one-step versus staged elevation.
- A recommendation tied to a competing option and a decisive falsifier, plus the grant-mutation receipt shape.
- Open Owner questions, explicitly including audit-retention/erasure and step-up cadence.

## Non-goals

- Do not grant, widen, revoke or simulate any real authority or credential.
- Do not reopen `OR-005`/`OR-014`, and do not promote a recommendation into an Owner decision.
- Do not decide audit-retention or audit-erasure policy.
- Do not edit constitution, auth, config, cron, spending or deployment state.
- Do not include private project identity, credentials, account identifiers or local paths.
- Do not equate a signature, edition name or preset with a capability grant.

## Completion gate

- Every capability claim is pinned to a primary source or explicitly marked unverified.
- The matrix covers each control-plane, credential, billing, publication, merge, deployment, service and grant-administration verb.
- Every recommendation names a competing option and a decisive falsifier.
- `OR-005`/`OR-014` questions are neither reopened nor promoted, and audit retention stays separate.
- No protected path is edited and no runtime/provider/auth/cron/PAUSE/spending effect occurs.
- The deliverable passes a privacy and secret scan with no identifiers or local paths.
- Owner questions are listed separately from model recommendations.
