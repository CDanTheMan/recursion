---
title: R-M — Claude Code terminal modding: adopt, port or avoid
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-M — Claude Code terminal modding: adopt, port or avoid

This is an upstream-capability study for accepted Owner decisions D-018, D-019, D-022, D-024 and
D-031, with D-021 and D-033 as constraints, and the gap register in
[GAPS.md](../../research-lane/GAPS.md). It examines the newly launched Claude Code **mods**
("terminal modding") capability and determines what Recursion can adopt, port or avoid; how it
relates to [R-K](R-K-terminal-multiplexer-and-tui.md) and
[R-L](R-L-interface-platform-cli-tui-gui.md); its licensing/terms boundary; and its decisive
falsifiers. It consumes the already accepted direction in
[INTERFACE-STRATEGY.md](../../INTERFACE-STRATEGY.md), [TERMINAL-RUNTIME.md](../../TERMINAL-RUNTIME.md),
[CLI.md](../../CLI.md) and [PERFORMANCE-PLAN.md](../../PERFORMANCE-PLAN.md); it must not reopen
their requirements.

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

- The capability under study is the Claude Code **mods** feature (described by its publisher as
  plugins whose behaviour lives in a JavaScript/TypeScript hooks module). It launched to general
  availability on **2026-10-01** for the Claude Code CLI and desktop app, requiring version
  **2.1.287** or later, and is described as on by default in that release. An earlier, gated
  early-access form used the environment variable `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`; the
  feature was named in an upstream issue on **2026-09-09**, and the first built-in mod
  (`agents-md`) is reported in version **2.1.277** on **2026-09-18**. **Re-pin every one of these
  facts to the exact official source and retrieval date before relying on it; treat any
  non-official summary as secondary and mark it as such.**
- Stated mechanics from the public announcement and tutorial, to be independently verified:
  a mod ships inside a Claude Code plugin; its behaviour lives in a module exporting
  `register(on, options)`; hooks attach to engine events with the shape `($, e, next)`; a hook can
  observe (call `next`), rewrite (`next({...e})`) or answer (return a result instead of calling
  `next`). Events named publicly include tool calls, the submitted prompt and prompt context,
  turn start/complete, session start/end, slash-command run, and a UI-render event covering the
  interface as it is drawn.
- Stated UI and API surface, to be verified: a mod can draw UI (panes, bands above the prompt,
  component trees), register slash commands, register tools the model can call, and act without
  spending model tokens. A `$` API is described as exposing surfaces including `ui`, `session`,
  `state`, `store`, `fs`, `process`, `clock`, `http`, `tool`, `command` and `model`. The
  publisher also states some of Claude Code's own features are built as mods (AGENTS.md support,
  a `/diff` pane, telemetry, an organisation security mod), with source published under a `mods/`
  directory in the upstream repository.
- Security and packaging, to be verified: mods are stated to run with the same machine access as
  Claude Code and **are not sandboxed**, are authored by their publisher rather than the vendor,
  and are installed and shared like plugins; validation and test commands exist. The API is
  stated to be able to change between releases without notice, and public documentation coverage
  was initially thin. Treat any per-hook latency figure quoted by the vendor as a vendor claim,
  not evidence.
- Adjacent, separately dated public facts that bear on Recursion's integration lanes: the
  upstream hook output includes an allowlisted `terminalSequence` field (reported in version
  2.1.141, **2026-05-13**) that routes BEL, OSC window-title and OSC notification sequences
  through the host's own terminal-write path; and a screen-reader mode prints plain linear text.
  Re-pin these before citing them.
- Relationship to this packet's lanes: R-K designs Recursion's own multiplexer and transformative
  TUI; R-L designs the shared command-and-query platform for CLI, TUI and later GUI. R-M asks
  whether an upstream in-engine modding model is **prior art** for either, a **candidate source**
  of notes or code patterns, or a **competing mechanism** to be deliberately avoided. It does not
  change R-K or R-L requirements.
- D-018 makes Recursion a native harness **and** a unifying wrapper with no ecosystem lock-in, so
  any adoption must be adapter-side and replaceable, never a hard dependency on one vendor's
  extension surface. D-019 means any adopted capability ships built but opt-in, not default.
- D-022 fixes one pause/stop vocabulary (Aggressive/Full/Lazy plus
  `checkpoint`/`interrupt`/`drain`): an in-engine hook that can deny or rewrite a call is **not**
  Recursion's Stop authority, and a host-side guard mod is not a permission system. A socket
  close or killed process is not external rollback.
- D-024 makes productive continuity the measurable differentiator; a hot-reloaded, in-session,
  vendor-unstable extension surface is at best accelerator state, not canonical recovery
  authority. D-031 forbids any vendor-sabotage claim and any unmeasured savings claim.
- D-021 and D-029 frame the credential boundary: this study must not propose collecting,
  copying or relaying upstream credentials, and a mod running with the host's full access is
  relevant only as a **negative** example relative to the trusted launch boundary.
- Evidence status: no mod was installed, built, run or benchmarked by Recursion for this lane.
  Much of the public detail is secondary reporting and a tutorial; the exact stable API, the
  license of the built-in mod source, the plugin/marketplace terms and the distribution rules are
  to be pinned or recorded as `unknown`.

## Purpose

Produce the decision-ready **Claude Code terminal-modding study** for Recursion: a pinned,
date-stamped account of what the capability is and exposes; a capability-by-capability
disposition of **adopt / port / avoid / watch** with a competing option, a decisive falsifier and
a non-proof for each; the licensing, terms and redistribution boundaries that constrain any
reuse; the relationship to R-K's multiplexer/TUI and R-L's command-and-query platform without
reopening either; and the precise negative traces that would eliminate a disposition. It delivers
findings with evidence classes and an explicit `unknown` list. It does not select a component,
vendor or extension mechanism, does not copy code, does not install or run anything, executes no
provider call, and makes no legal conclusion.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, store, framework, runtime, extension mechanism, plugin format, transport, UI toolkit,
renderer or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-021, D-022,
D-024 or D-033. Do not assert unreleased, undocumented or unstable behaviour as fact; mark it
`unknown` or `inferred` and keep the evidence class visible. Do not reproduce or vendor upstream
source or licence text beyond short, attributed, fair quotation. No mod is installed, built, run,
tested or benchmarked; no provider, model or account call is made; no credential or account is
touched. Do not present a host-side guard mod as a permission or Stop authority (D-022), and do
not claim measured performance, security or savings.

## Inputs to read

None from this repository: the rescope, the accepted interface, terminal, CLI and performance
requirements and the D-018/D-019/D-021/D-022/D-024/D-031 context are summarized in
`## Baked context` above, and no repository, connector or private-source access is assumed. The
session must, however, retrieve and pin the public sources it cites — the official Claude Code
mods announcement and tutorial, the official Claude Code plugin and marketplace documentation,
the public `mods/` source directory and its repository licence, the relevant changelog and
release notes, the plugin security documentation, and any `terminalSequence` and screen-reader
documentation it cites — and pin each claim to a URL, version and retrieval date. Prefer primary
sources over secondary summaries; where only secondary reporting exists, label it.

## Research questions

### What the capability is

1. What exactly is a Claude Code mod at the pinned version: its packaging, the
   `register`/`on`/hook model, the event catalogue, the observe/rewrite/answer semantics, and the
   lifecycle (load, hot reload, session scope, isolation)? Separate source-documented facts from
   tutorial examples and secondary reporting.
2. What does the `$` API expose and what can a mod actually change — prompts, tool calls,
   streamed output, UI component trees, registered slash commands and tools — and what is
   explicitly not modifiable? Mark anything not shown by a primary source as `unknown`.
3. What is the stated stability contract, version pinning, type-declaration mechanism and
   validation/testing path, and what does "may change between releases without notice" imply for
   any dependency on it?

### Adopt, port or avoid

4. Which concepts are worth **adopting** as design prior art for R-L (an event-driven hook model,
   an answer/rewrite distinction, a declarative UI tree, plugin packaging, hot reload) and for
   R-K (panes, above-prompt bands, redraw-on-subscription), each with a competing option and a
   falsifier?
5. Which artefacts, if any, are candidates for **porting** (with measured or estimated cost, per
   D-033) versus clean-room reimplementation, given an unstable API and unknown licence? What
   would make porting cheaper than a native design, and what would falsify that?
6. Which behaviours must Recursion **avoid**: in-engine unsandboxed execution with host access,
   hot reload of an in-session module, dependence on an undocumented/unstable API, a guard mod
   mistaken for a permission system, or a second admission path that bypasses Recursion's
   command schema?
7. How does a vendor-specific in-process extension surface sit against D-018's no-lock-in and
   D-021/D-029's credential boundary, and what is the decisive negative trace for each
   disposition?

### Licensing, terms and security

8. What is the exact repository and plugin licence for the public mods source, and what does it
   permit for reading, adapting or redistributing? What do the plugin and marketplace terms say,
   and what remains a counsel question (G-32 / D-027) rather than a research conclusion?
9. What are the documented security properties and known limitations — same-access execution,
   absence of a sandbox, publisher trust, guard-mod bypasses — and how do they inform Recursion's
   own plugin-isolation and known-safe-refusal design without endorsing or copying them?
10. What does this study **not prove**: that any capability is stable, licensed for reuse,
    performant, accessible, sandboxed, or portable into Recursion?

### Relationship to R-K and R-L

11. How does an upstream in-engine modding model compare with Recursion's planned
    plugin-contributed views and commands in R-L: is it complementary, competing, or a
    different trust tier, and what does R-L learn from its typed event/answer model?
12. How do upstream UI primitives (panes, above-prompt bands, redraw-on-subscription, screen
    reader text, OSC notification/title sequences) inform R-K's non-flicker rendering,
    follow-mode and accessibility contract, and which of these are already existing affordances
    rather than novelty?

### Falsifiers and acceptance

13. For every adopt/port/avoid disposition, what is the decisive falsifier — the specific
    observed fact that reverses it — and the provider-free check that demonstrates it without
    installing or running a mod or making any provider call?
14. What provider-free acceptance fixtures or evidence checks would let an independent verifier
    accept the study's dispositions, and what would show the study merely repeated vendor
    marketing?

## Deliverable

A Claude Code terminal-modding study containing: a **pinned capability account** with exact
versions and dates (mods GA 2026-10-01, version 2.1.287, early-access and built-in-mod dates,
each with its primary source or an explicit `unknown`); a **surface map** of the event model, the
`$` API, UI primitives, command/tool registration, validation/testing and stability contract,
with evidence classes per row; an **adopt / port / avoid / watch ledger** in which every entry
names a competing option, a decisive falsifier and what it does not prove; an **licensing and
terms** section that states what is source-documented and defers every legal conclusion to
counsel (G-32); a **security** section that treats same-access unsandboxed execution as a
negative example for Recursion's own boundary; a **relationship** section that ties findings to
R-K and R-L without reopening them; and a **provider-free evidence/acceptance** section. It
selects no component, mechanism or vendor and copies no code.

## Non-goals

- No selection of a language, store, framework, runtime, extension mechanism, plugin format,
  transport, UI toolkit, renderer or vendor.
- No installation, build, run, test or benchmark of any mod, plugin, marketplace or Claude Code
  binary; no provider, model, credential or account call; no network action beyond reading
  public documentation.
- No legal or licensing conclusion; per-route and per-artifact terms remain counsel-gated
  (G-32 / D-027), and no code, licence text or long quotation is reproduced.
- No assertion of unreleased, undocumented or unstable behaviour as fact, and no claim that a
  host guard mod is a permission system or a Stop authority.
- No claim of measured performance, security, accessibility or savings; no vendor-sabotage claim
  (D-031).
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that porting an existing extension, plugin or interface is cheap; it remains a
  hypothesis with a falsifier (D-033).
- No new executive tier, no separate AI "ARM manager", and no second portfolio executive.
- No reopening of D-018, D-019, D-021, D-022, D-024, D-031 or D-033, and no reopening of the
  accepted requirements in `INTERFACE-STRATEGY.md`, `TERMINAL-RUNTIME.md`, `CLI.md` or
  `PERFORMANCE-PLAN.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The capability account pins the feature's general-availability date and minimum version, the
  early-access and first built-in-mod dates, and the event/API surface, each to a primary public
  source with a retrieval date or an explicit `unknown`; secondary-only claims are labelled.
- The adopt / port / avoid / watch ledger covers the event-hook model, `answer`/`rewrite`
  semantics, declarative UI primitives, plugin packaging, hot reload, in-engine unsandboxed
  execution, unstable API and second-admission-path risk, and every entry names a competing
  option, a decisive falsifier and what it does not prove.
- The licensing and terms section states the exact source-documented licence and plugin terms it
  could pin and defers every legal conclusion to counsel (G-32 / D-027); no code is copied.
- The security section records same-access unsandboxed execution, publisher trust and guard-mod
  limitations as evidence, and does not present them as Recursion's permission or Stop authority
  (D-022).
- The relationship section states how the upstream model compares with R-L's plugin-contributed
  views/commands and R-K's rendering/accessibility contract, and whether each is complementary,
  competing or already existing, without reopening R-K or R-L.
- A provider-free evidence/acceptance section specifies how an independent verifier accepts the
  dispositions without installing or running a mod and without a provider call.
- The study explicitly states what it does not prove: no stability, licence fitness,
  performance, accessibility, sandboxing, portability, entitlement or measured savings.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no component, mechanism or vendor is selected and no route is qualified.
- Protected paths are untouched; privacy and secret scan are clean.
