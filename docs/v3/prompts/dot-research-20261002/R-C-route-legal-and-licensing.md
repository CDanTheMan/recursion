---
title: R-C — Per-route terms, credential limits and Recursion's licensing posture
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-C — Per-route terms, credential limits and Recursion's licensing posture

This is a rescope handoff for accepted Owner decisions D-021, D-026 and D-027, and the gap
register in [GAPS.md](../../research-lane/GAPS.md).

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
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

- D-021 accepts delegation over credential intermediation and states explicitly that third-party
  credential intermediation is the specific thing provider terms restrict, while per-route terms
  and automation limits remain counsel-gated (G-32 / D-027).
- D-026 chooses Apache-2.0 for Recursion's own release, with the plugin/capability contract
  published early, and a contribution/CLA posture still to be finalized; the decision notes it is
  a distribution decision that still requires counsel before any public release claim.
- D-027 authorizes preparation of a counsel-ready packet covering per-route terms/ToS, third-party
  credential-intermediation limits, Recursion's own licensing, and distribution and trademark
  handling. Lucas engages counsel; no spending or legal commitment is made by an agent.
- Named harnesses and routes referenced in this repository include Claude Code, Codex/ChatGPT,
  Cursor, Gemini/Google CLI, Grok Build, Hermes, OpenCode, Antigravity and Pi, among others.
  Public reference work found that some carry permissive licenses while at least one public
  repository uses proprietary commercial terms; individual repository licenses do not license
  external services, and all such facts are mutable.
- G-32 remains open until counsel returns. This lane prepares the question packet; it does not
  answer it and it does not give legal advice.

## Purpose

Produce a counsel-ready question packet that identifies, per route and per distribution choice,
the terms-of-service, credential-intermediation and distribution constraints Recursion must
respect, and the licensing posture questions the project itself must resolve. This is legal-risk
research and **not legal advice**. It gathers and classifies public evidence and formulates
precise questions for a qualified lawyer; it makes no legal conclusion, no infringement finding
and no clearance statement. No spend and no counsel contact is performed by the session.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **This is legal-risk research, NOT legal
advice. Do not make legal conclusions, do not opine on whether a route is lawful, do not clear or
condemn any practice.** Do not select a license, a route, a vendor, a distribution model or a
trademark as a product default. No credential is collected or displayed; no login, provider call,
purchase or legal engagement occurs. Do not decide an Owner question recorded in D-021, D-026 or
D-027. All questions must be phrased for a qualified lawyer to answer.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Per-route terms and credential posture

1. For each named route — Claude Code, Codex/ChatGPT, Cursor, Gemini/Google CLI, Grok Build,
   Hermes, OpenCode, Antigravity and Pi, and any other route the operator names — what do the
   public terms of service, acceptable-use policies and automation provisions say about
   programmatic or headless use, non-interactive use, resale, and driving a locally installed,
   user-authenticated client, stated as quotations with retrieval dates and `unknown` where the
   term is absent or ambiguous?
2. Which routes, on the public record only, distinguish **driving an installed, user-authenticated
   CLI** from **a third party holding, storing or relaying the user's credential**, and where does
   that distinction remain `unknown`?
3. What documented restrictions exist on generating or reselling access, on routing a user's
   subscription through another product, on quota or rate-limit circumvention, and on
   redistribution of bundled assets or binaries, again as quoted public evidence rather than
   conclusions?
4. What is documented about account, entitlement and identity: whether an API key, a
   subscription session and a CLI login are treated as distinct, and which identity a delegated
   route would present?

### Distribution, trademark and bundled assets

5. What public licensing, notice, trademark and attribution terms attach to each named route's
   source, binaries, names and logos, and which are `unknown`?
6. For an Apache-2.0 product that ports or interoperates with other ecosystems, what public
   obligations are stated for notices, patent grants, trademark use, bundled third-party assets,
   plugin-package redistribution and SBOM provenance — stated as candidate obligations for
   counsel, not as advice?
7. What distribution choices (bundling a wrapper, shipping only adapters, naming interoperability
   in prose, shipping a plugin contract without third-party code) raise which open questions, and
   what public examples show different postures?

### Recursion's own licensing posture

8. Given D-026's Apache-2.0 choice and an early plugin-contract publication, what open questions
   remain for counsel about contribution licensing, a contributor agreement, a plugin-sdk or
   interface license, trademark of the project name, third-party notice assembly, and
   compatibility with permissive upstream licenses?
9. What competing licensing postures exist (for example permissive versus copyleft for the
   contract or the plugins, an SPDX-identified interface license, or a separate trademark
   policy), and what does each not resolve without counsel?
10. What precise questions must the counsel packet answer to close G-32, and what evidence
    appendix should accompany each question?

## Deliverable

A source-pinned, counsel-ready question packet containing: a per-route evidence table (quoted
public term, source URL, retrieval date, classification `source-documented`/`unknown`,
expiry trigger); a distribution/trademark/bundled-asset evidence table; a licensing-posture
question set for Recursion itself; and an explicit list of the questions only qualified counsel
can answer. Every entry is framed as a question or quoted evidence, never as a legal conclusion.
Each proposed posture names a competing option and what it does not resolve. No route, license or
distribution model is selected.

## Non-goals

- No legal advice and no legal conclusion, clearance or infringement finding.
- No selection of a license, route, vendor, distribution model or trademark.
- No credential collected or displayed; no login, provider call, purchase or counsel engagement.
- No claim that a public term permits or forbids a practice; ambiguous terms are `unknown`.
- No decision of G-32, D-021, D-026 or D-027.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every named route has a terms/credential evidence row with quoted public sources and retrieval
  dates, or an explicit `unknown`.
- The driving-an-installed-CLI versus credential-intermediation distinction is stated per route
  from public evidence only.
- Distribution, trademark, notice and bundled-asset questions are separate from license
  questions.
- Recursion's own licensing posture is expressed as open questions, not decisions.
- Every conclusion-shaped statement is reframed as a question for counsel; no legal conclusion
  appears.
- The packet names competing postures and what each leaves unresolved.
- Protected paths are untouched; privacy and secret scan are clean.
