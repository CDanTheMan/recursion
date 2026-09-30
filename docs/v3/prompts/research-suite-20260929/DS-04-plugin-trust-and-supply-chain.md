---
title: DS-04 — Plugin trust and supply chain
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

# DS-04 — Plugin trust and supply chain

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

- **Focus.** This lane defines what a maintainer signature actually proves and how unsigned local plugins can keep full expressiveness without silent supply-chain failure, so the plugin trust and grant contract can be frozen. It is research lane R6 of the Recursion v3 agenda.
- **Trust root.** The installation trust root signs first-party/maintainer-approved releases and plugins. `OR-007` ratifies maintainer-signed trust and a digest-aware acknowledgement. A valid signature proves publisher/review-policy identity, not that every requested capability is safe for every project; signatures, SBOMs and transparency records do not prove benign runtime behavior or spending entitlement.
- **Unsigned local plugins.** They remain installable and may implement the complete plugin API. The CLI warns that they are not maintainer approved, pins the exact digest and displays all requested authority. `OR-007` requires a digest-specific warning/acknowledgement, and installing code must not silently imply unlimited quota or metered authority.
- **Separate grant dimensions.** Functional API verbs, OS/workspace scope, network egress, credential access, model launch, route/account, subscription quota, metered spending, update, downgrade and revocation each remain separately visible and configurable. `OR-014` makes digest-aware plugin grants a common default.
- **Trust tiers.** `T0-kernel`, `T1-signed-built-in`, `T2-signed-isolated-third-party`, `T3-untrusted-view`, and `T4-external-engine/provider`. A tier is an isolation and review requirement, never an authority grant.
- **Lifecycle.** discovered -> verified -> admitted -> staged -> active, with quarantined/rejected branches and drain-and-fence on retire, replace or revoke. Reload is a fenced transition; stale packets, leases and subscriptions fail closed; ambiguous external effects enter reconciliation and never become success.
- **Revocation semantics.** Revocation blocks new admission immediately; existing work follows its effect-specific PAUSE policy and may enter reconciliation. "revoked" does not assert that a remote effect stopped.
- **Owner sovereignty.** There is no mandatory centralized marketplace, remote kill switch or maintainer veto; a design must never let a remote maintainer disable or update a local owner's installation against the owner's configured intent.
- **Disabled-plugin invariant.** A disabled plugin performs no import, install, subprocess, network, credential, model or quota effect.

## Purpose

This research informs what a maintainer signature actually proves and how unsigned local plugins can keep full expressiveness without silent supply-chain failure, so the plugin trust and grant contract can be frozen. It is blocking because `OR-007` ratifies a maintainer-signed trust root and digest-aware acknowledgement while leaving the relationship between one acknowledgement and separate quota, spending, route, update and revocation grants unresolved. A remote maintainer must never gain veto over a local owner's installation.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. This lane may not install, sign, publish or update any plugin, and it must not treat a signature, SBOM or transparency record as proof of benign runtime behavior or of spending entitlement.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. What does maintainer signing by the installation trust root actually prove about publisher/review identity, and what does it not prove about runtime behavior, project fit or quota entitlement?
2. How can unsigned local plugins retain full feature expressiveness after a digest-specific warning/acknowledgement rather than warning-only supply-chain failure?
3. Which concrete prior systems (package signing, TUF, SLSA provenance, Sigstore, lockfiles, SBOMs, sandbox/WASI capability models) give enforceable identity, traceability and freshness — with pinned versions and stated limits?
4. Which grant dimensions must stay separate — functional API verbs, OS/workspace scope, network egress, credential access, model launch, route/account, subscription quota, metered spending, update, downgrade and revocation?
5. Can one digest-specific acknowledgement safely mint requested grants, or is staged consent required, and what policy keeps the novice path simple without silent spending authority?
6. How should dependency-confusion, update compromise, rollback and unmaintained-source risks be represented, tested and quarantined without a mandatory remote kill switch?
7. What is the exact reload/update/revocation lifecycle (discover, verify, admit, stage, drain, fence, retire), and how do stale packets, leases and subscriptions fail closed?
8. How is the trust tier (kernel, signed built-in, signed isolated third-party, untrusted view, external engine) kept as an isolation/review requirement rather than an authority grant?
9. What deterministic tests prove that a disabled plugin performs no import, install, process, network, credential, model or quota effect?
10. What prevents a remote maintainer from vetoing, disabling or updating a local owner's unsigned plugin against the owner's configured intent?
11. What competing option (mandatory central registry with remote revocation) fails, and by what decisive falsifier tied to owner sovereignty?
12. How are version support windows, rollback and security-emergency refusal represented as configurable policy rather than silent expansion?

## Deliverable

- A source-pinned claim table classifying each trust/supply-chain mechanism by what it proves, confidence and expiry.
- A grant-dimension matrix showing separate versus shared acknowledgement, with per-dimension falsifiers.
- A lifecycle and failure-containment table for install, reload, update, revocation and quarantine.
- A recommendation tied to a competing option and a decisive falsifier, plus open Owner questions.

## Non-goals

- Do not install, sign, publish, update or execute any plugin or package.
- Do not reopen `OR-007`/`OR-014`, and do not select which dimensions share one acknowledgement.
- Do not introduce a mandatory central marketplace, remote kill switch or maintainer veto.
- Do not treat a signature, SBOM or transparency record as a safety verdict or spend grant.
- Do not edit constitution, auth, config, cron or plugin manifests.
- Do not include private project identity, credentials or local paths.

## Completion gate

- Every trust claim is pinned to a primary source or explicitly marked unverified, with license noted.
- The grant matrix covers every listed dimension separately and shows where sharing is safe or unsafe.
- Every recommendation names a competing option and a decisive falsifier.
- Owner sovereignty is preserved: no design grants a remote maintainer veto over a local owner.
- `OR-007` is neither reopened nor promoted; shared-acknowledgement choice remains an Owner question.
- No protected path is edited and no runtime/provider/auth/cron/PAUSE/spending/install effect occurs.
- The deliverable passes a privacy and secret scan; Owner questions are listed separately.
