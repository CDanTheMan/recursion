---
title: R-G — Importing existing plugin ecosystems and cross-harness plugin reuse
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-G — Importing existing plugin ecosystems and cross-harness plugin reuse

This is a rescope handoff that extends R-A for accepted Owner decisions D-019, D-026 and D-033,
with the gap register in [GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-A](../../../../docs/v3/prompts/dot-research-20261002/R-A-plugin-portability.md), the
plugin/capability contract handoff, and must extend rather than restate it.

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

- D-019 chooses to build the comprehensive capability and plugin surface but ships every
  capability as an opt-in plugin or profile rather than a default. Its consequence states that a
  large fraction of that surface is port/optimize work ported from existing plugin ecosystems,
  not new invention.
- D-026 chooses Apache-2.0 for Recursion's own release with the plugin/capability contract
  published early to attract porters, and a contribution/CLA posture still to be finalized. It is
  a distribution decision that still requires counsel before any public release claim.
- D-033 treats "porting is cheap" strictly as a **hypothesis to validate, not assume**: R-A found
  porting savings unmeasured and an acceptable-port count of zero possible. This lane is
  commissioned to test that hypothesis. Its falsifier is that measured porting cost exceeds a
  native rewrite, or that no ecosystem imports cleanly.
- R-A's proposed contract covers identity, schema epoch, declared contributions, required and
  granted capabilities, authority attenuation, privacy classification, budget and egress bounds,
  and the evidence/output contract, with a capability graph whose grants can never widen a
  constitutional boundary. This lane must extend that contract, not replace it.
- R-A's porting-cost model uses per-ecosystem effort bands, glue-LOC, adapter surface count,
  capability-translation steps and conformance failures, with denominators and uncertainty
  ranges. This lane must validate or falsify that model rather than assert it.
- Ecosystems in scope as prior art: DeepSeek Harness / Cordis first, then OpenCode (v1 and v2),
  Goose extensions, the Model Context Protocol (MCP) and the VS Code extension model. The public
  OpenAI, Anthropic and Cursor extension surfaces and T3 Code, Hermes Agent and Pi may be cited
  where relevant.
- Evidence status: R-A found no porting-cost measurement exists. The honest status of every
  "shared manifest / generated adapter" economy is unmeasured; this lane's job is to design
  measurable methods, not to claim savings.

## Purpose

Produce the decision-ready evidence pack that determines whether Recursion's plugin/capability
contract can be a superset that imports and translates existing plugin ecosystems, and whether a
single plugin can serve multiple harnesses. The lane assesses importability per ecosystem — with
DeepSeek Harness / Cordis first, then OpenCode, Goose, MCP and VS Code — designs a translation
layer over R-A's contract, names what cannot be translated, proposes a porting-cost validation
approach, and supplies decisive falsifiers. "Porting is cheap" is treated strictly as a
hypothesis. This is a research and contract-design lane: it does not select a language, store,
framework, runtime or vendor, does not implement a loader and does not install or execute any
third-party plugin.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, sandbox, plugin runtime, store or vendor.** Do not claim that any
upstream ecosystem is certified, supported, stable or CVE-free. No installer runs, no plugin
executes, no network effect is performed and no credential is requested. Do not decide an Owner
question recorded in D-019, D-026 or D-033. Treat DeepSeek Harness Cordis, OpenCode, Goose, MCP,
VS Code and the OpenAI/Anthropic/Cursor surfaces as prior art cited from public sources, not as
endorsed or selected components.

## Inputs to read

None. This handoff is self-contained; the rescope, R-A's contract summary and prior conclusions
are summarized in `## Baked context` above. Do not assume repository, connector or private-source
access.

## Research questions

### Importability assessment per ecosystem

1. For each named ecosystem — DeepSeek Harness (Cordis) first, then OpenCode v1, OpenCode v2,
   Goose extensions, MCP and VS Code extensions — what is the documented plugin unit, manifest
   schema, discovery mechanism, lifecycle, permission or capability declaration, and contribution
   points, and which are `unknown` because only marketing or partial source is public?
2. For each ecosystem, what is the documented or source-visible distance to R-A's contract: which
   fields map directly, which map with a mechanical transformation, which need a semantic
   annotation, and which have no counterpart?
3. Which ecosystem should be imported first for the highest validated leverage, and what evidence
   (manifest expressiveness, license clarity, interface stability, population of existing plugins)
   supports that ranking?
4. What cannot be translated at all — host-specific glue, runtime assumptions, undocumented
   internal APIs, UI contributions, lifecycle hooks with no counterpart, or licensed
   assets — and how should the contract represent "unportable" rather than pretend to cover it?

### Translation layer design

5. What translation layer maps a foreign manifest to R-A's manifest and capability graph in a way
   that is mechanical, inspectable and reversible where possible, and that never lets a translated
   grant widen authority, privacy, egress, credential visibility, billing or publication?
6. How should the contract represent partial imports (capability present but degraded), so that a
   translation failure is visible as a declared loss rather than a silent omission?
7. Can one Recursion plugin serve multiple harnesses — a single capability with per-harness
   adapters — and what is the documented shape of a multi-host contribution in the named
   ecosystems that would or would not support this?
8. What normative versus adapter-local boundaries must R-A's contract add so that imported
   ecosystems do not leak host-specific concepts into the canonical contract?

### Porting-cost validation and cross-harness reuse

9. How can R-A's porting-cost model be validated or falsified with a concrete, provider-free
   method — a synthetic multi-ecosystem fixture set, a counted translation checklist, glue-LOC and
   adapter-surface measurement, and conformance failures as the dependent variable?
10. What is the cheapest credible porting path per ecosystem under the extended contract, and what
    is the competing option (native rewrite, one-way shim, generated adapter, or no port)?
11. Which cross-harness reuse economies are real (shared manifest, shared contribution taxonomy,
    generated adapters, one plugin many hosts) and which are speculative, and what would falsify
    each?
12. What decisive falsifiers would show that "porting is cheap" is false — measured cost above a
    native rewrite, zero cleanly importing ecosystems, or translation that loses authority,
    privacy or evidence semantics?

## Deliverable

A source-pinned report containing: an importability matrix per named ecosystem whose every cell is
source-documented, inferred or `unknown`; an extension of R-A's plugin manifest and
capability-graph contract with a translation-layer design and explicit normative versus
adapter-local boundaries; an explicit list of what cannot be translated and how it is represented;
a porting-cost validation approach that turns R-A's model into a measurable, provider-free
procedure with denominators and uncertainty ranges; a cross-harness reuse assessment (one plugin,
many harnesses); and decisive falsifiers. "Porting is cheap" appears only as a hypothesis with a
falsifier. Each recommendation names a competing option and what it does not prove. No language,
store, framework, runtime or vendor is selected.

## Non-goals

- No selection of a language, package manager, sandbox, plugin runtime, store or vendor.
- No installer executed, no plugin loaded, no network effect, no credential handled.
- No claim that any upstream ecosystem is certified, supported, stable or CVE-free.
- No implementation of a Recursion loader, translation engine or capability engine.
- No assertion that porting is cheap; it remains a hypothesis with a falsifier.
- No legal conclusion about licenses or distribution (that belongs to R-H and counsel).
- No reopening of D-019, D-026 or D-033.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Every named ecosystem has an importability assessment with manifest, discovery, lifecycle,
  permissions and contributions, each cell source-documented, inferred or `unknown`.
- The translation layer is described as a concrete mapping onto R-A's manifest and capability
  graph and cannot widen a constitutional boundary.
- What cannot be translated is listed explicitly, with a contract representation for loss.
- Cross-harness reuse (one plugin, many harnesses) is assessed with evidence, not assumed.
- The porting-cost validation approach is provider-free and measurable, with denominators,
  uncertainty ranges and conformance failures as the dependent variable.
- "Porting is cheap" appears only as a hypothesis, and each claim carries a decisive falsifier.
- Every recommendation names a competing option and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.
