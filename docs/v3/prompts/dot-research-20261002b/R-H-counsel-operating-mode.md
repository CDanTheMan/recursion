---
title: R-H — Counsel-ready packet for the caller-of-the-CLI operating mode
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-H — Counsel-ready packet for the caller-of-the-CLI operating mode

This is a counsel-ready handoff that extends R-C for accepted Owner decisions D-030, D-021 and
D-031, within D-027's authorization, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It builds on
[R-C](../../../../docs/v3/prompts/dot-research-20261002/R-C-route-legal-and-licensing.md), the
per-route terms and licensing handoff, and must extend rather than restate it. G-32 remains open
until counsel returns.

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

- The exact operating mode to be reviewed: Recursion owns the JSON stream of the user's
  authenticated CLI/headless output; it is a caller of that CLI, not a provider proxy; there is
  one place to connect keys/subscriptions; routing and fan-out happen via the harness's own
  native features inside the user's own subscription.
- D-030 accepts this delegation model subject to counsel, with the falsifier that counsel finds it
  indistinguishable from credential intermediation on a required route, or a harness forbids
  third-party drivers. D-030 is exactly the open question this lane prepares for counsel.
- D-021 accepts delegation over credential intermediation and states that third-party credential
  intermediation is the specific thing provider terms restrict; driving the user's
  already-authenticated CLI is preferred over capturing OAuth tokens. Per-route terms and
  automation limits remain counsel-gated (G-32 / D-027).
- D-031 chooses not to market on a vendor-sabotage claim: Recursion is positioned on its
  unrestrictive, customizable environment, one place to connect keys/subscriptions, routing
  through any harness or its own, with privacy and safety; savings are claimed only when measured
  (R-D).
- D-026 chooses Apache-2.0 for Recursion's own release and an early plugin-contract publication;
  this is a distribution decision that still requires counsel. Referenced in this lane only as
  posture, not to be decided here.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — Aggressive / Full / Lazy — plus `checkpoint`, `interrupt` and `drain`. The
  counsel packet should describe the stop/revocation capability in that vocabulary.
- Named routes in scope: Claude Code, Codex/ChatGPT, Cursor, Gemini/Google CLI, Grok Build, Hermes,
  OpenCode, Antigravity and Pi, and any other route the operator names. Public reference work found
  that some carry permissive licenses while at least one public repository uses proprietary
  commercial terms; individual repository licenses do not license external services, and all such
  facts are mutable.
- Evidence status: G-32 remains open until counsel returns. This lane prepares the question packet;
  it does not answer it and it does not give legal advice.

## Purpose

Produce a source-pinned, counsel-ready question packet for the exact operating mode in which
Recursion owns the JSON stream of the user's authenticated CLI/headless output, is a caller rather
than a provider proxy, offers one place to connect keys/subscriptions, and routes and fans out via
harness-native features. The packet asks counsel whether this is distinguishable from prohibited
credential intermediation and automation per route, what conditions attach, and what public
distribution posture is safe (adapter-only, no bundled vendor binaries, no credential custody). It
extends R-C and keeps G-32 open. This is legal-risk research and **not legal advice**. It makes no
legal conclusion, no clearance statement and no infringement finding; no spend and no counsel
contact is performed by the session.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **This is legal-risk
research, NOT legal advice. Do not make legal conclusions, do not opine on whether a route is
lawful, and do not clear or condemn any practice.** Do not select a license, route, vendor,
distribution model or trademark as a product default. No credential is collected or displayed; no
login, provider call, purchase or counsel engagement occurs. Do not decide an Owner question
recorded in D-021, D-026, D-027, D-030 or D-031, and do not close G-32. All questions must be
phrased for a qualified lawyer to answer.

## Inputs to read

None. This handoff is self-contained; the rescope, R-C's scope and prior conclusions are summarized
in `## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### The operating mode and the intermediation boundary

1. What public terms, policies and automation provisions, quoted with retrieval dates, bear on
   each named route when a local product (a) launches the user's installed, user-authenticated CLI,
   (b) parses that CLI's own stdout/JSON, (c) holds no credential, and (d) offers one place to
   connect keys/subscriptions — and where is the applicable term absent or ambiguous (`unknown`)?
2. On the public record only, which routes distinguish **driving an installed, user-authenticated
   CLI** from **a third party holding, storing or relaying the user's credential**, what language
   draws that line, and where does the distinction remain `unknown`?
3. What documented restrictions touch high-volume fan-out through a harness's own delegation
   features inside the user's subscription — rate limits, automation caps, simultaneous-session
   rules, resale or routing of subscription access, and quota-circumvention language — quoted per
   route?
4. Which identity does a delegated route present (API key, subscription session, or CLI login),
   how are those treated as distinct on the public record, and what does that imply for an
   accounting model in which the user's subscription is debited?

### Conditions, posture and distribution

5. What conditions, if any, attach to the operating mode per route — attribution, notice, a
   required "powered by" statement, an API-only requirement, a prohibition on headless use, or a
   requirement that the vendor's own client remain the only driver — stated as questions and quoted
   evidence, never conclusions?
6. What public-distribution postures are least exposed for an Apache-2.0 project: shipping only
   adapters, shipping no bundled vendor binaries or assets, providing no credential custody, naming
   interoperability in prose, and shipping a plugin contract without third-party code — and what
   open question does each leave?
7. What distribution choices raise the greatest open risk (bundling a wrapper around a vendor
   binary, redistributing vendor assets, naming or branding that implies endorsement, or enabling a
   route whose terms are unclear), and what competing postures avoid it?
8. What is the precise, answerable question set for counsel to determine whether the operating mode
   is distinguishable from prohibited credential intermediation on a required route, and what
   evidence appendix (quoted term, URL, retrieval date, expiry trigger) accompanies each question?

### Coach-readiness across R-C and G-32

9. How does this packet extend R-C rather than duplicate it — which R-C questions remain and which
   new operating-mode questions are added?
10. What conditions must be met before G-32 can close, and what would counsel need to confirm about
    the caller-not-proxy posture, harness-native fan-out, and distribution posture?
11. What competing legal interpretations exist (caller-of-installed-tool versus credentialed
    intermediation; subscription routing versus account sharing) and what does each leave
    unresolved without counsel?
12. What must the packet avoid so that it stays evidence-and-questions only — no legal conclusion,
    no clearance, no advice, no route decision — while still being directly usable by counsel?

## Deliverable

A source-pinned, counsel-ready question packet containing: a per-route evidence table for the
operating mode (quoted public term on driving an installed CLI, third-party credential
intermediation, automation and fan-out, one-place key/subscription connection, source URL,
retrieval date, classification `source-documented`/`unknown`, expiry trigger); a
distribution-posture question table for an adapter-only, no-bundled-binaries, no-credential-custody
release; an explicit list of the questions only qualified counsel can answer, each with its
evidence appendix; and a statement of how the packet extends R-C and what must be true to close
G-32. Every entry is framed as a question or quoted evidence, never as a legal conclusion; the
stop/revocation capability is described in the D-022 vocabulary. Each proposed posture names a
competing option and what it does not resolve. No route, license or distribution model is
selected.

## Non-goals

- No legal advice and no legal conclusion, clearance or infringement finding.
- No selection of a license, route, vendor, distribution model or trademark.
- No credential collected or displayed; no login, provider call, purchase or counsel engagement.
- No claim that a public term permits or forbids a practice; ambiguous terms are `unknown`.
- No decision of G-32, D-021, D-026, D-027, D-030 or D-031.
- No reinterpretation of the operating mode as credential custody; it remains caller-not-proxy.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every named route has an operating-mode evidence row with quoted public sources and retrieval
  dates, or an explicit `unknown`.
- The driving-an-installed-CLI versus credential-intermediation distinction is stated per route
  from public evidence only.
- Fan-out and subscription-routing terms are quoted per route, with `unknown` where absent.
- Distribution posture is expressed as separate open questions (adapter-only, no bundled binaries,
  no credential custody), not as a decision.
- Every conclusion-shaped statement is reframed as a question for counsel; no legal conclusion
  appears.
- The packet states how it extends R-C and what must be true to close G-32.
- The stop/revocation capability is described in the D-022 vocabulary.
- Each proposed posture names a competing option and what it leaves unresolved.
- Protected paths are untouched; privacy and secret scan are clean.
