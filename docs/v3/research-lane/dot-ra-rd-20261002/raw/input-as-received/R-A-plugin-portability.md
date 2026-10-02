---
title: R-A — Plugin and capability-graph contract for cheap porting
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v2-execution-fabric
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-A — Plugin and capability-graph contract for cheap porting

This is a rescope handoff for accepted Owner decisions D-018, D-019 and D-026, and the gap
register in [GAPS.md](../../research-lane/GAPS.md).

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

- D-018 reframes Recursion as both a first-class native harness and a first-class wrapper over
  the wider harness ecosystem, whose purpose is to remove lock-in and cut quota/usage burn,
  shipped as a community, open-source product.
- D-019 chooses to build the comprehensive capability and plugin surface, but ships every
  capability as an opt-in plugin or profile rather than a default. Its consequence states that a
  large fraction of that surface is port/optimize work ported from existing plugin ecosystems,
  not new invention.
- D-026 chooses Apache-2.0 and an early publication of the plugin/capability contract to attract
  porters. D-027 authorizes a counsel-ready packet only.
- The relevant public reference systems named in this repository include DeepSeek Harness
  (Cordis plugin kernel), OpenCode v1 and v2, Goose extensions and MCP, the Model Context
  Protocol, VS Code extensions, and the public OpenAI, Anthropic and Cursor extension surfaces.
  A pinned, source-documented reference matrix considers DeepSeek Harness, T3 Code, Hermes Agent,
  Pi and OpenCode to carry permissive licenses, while at least one harness uses proprietary
  commercial terms. Version, license and interface facts are mutable and must be re-pinned.
- This lane is a prerequisite for the plugin/route fabric and for the portability claim that
  underlies D-018 and D-019: if porting an existing extension is expensive, the product thesis is
  weakened. No porting-cost measurement exists yet; the honest status is unmeasured.

## Purpose

Produce the decision-ready evidence pack for a Recursion plugin manifest and capability-graph
contract that is optimized for cheap porting of existing extension ecosystems, together with a
porting-cost model and a falsifiable conformance-test design. This is a research and contract
design lane: it compares published extension models, proposes a portable contract, and specifies
inertness and conformance requirements. It does not select a language, store, framework or
vendor, does not implement a loader, and does not install or execute any third-party plugin.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select a language, package manager,
sandbox, plugin runtime, store, or vendor.** Do not claim that any upstream harness is certified,
supported, stable or CVE-free. No installer runs, no plugin executes, no network effect is
performed and no credential is requested. Do not decide an Owner question recorded in D-018
through D-027. Treat DeepSeek Harness Cordis, OpenCode, Goose, MCP, VS Code, and the
OpenAI/Anthropic/Cursor surfaces as prior art to be cited from public sources, not as endorsed or
selected components.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Extension-model comparison

1. For each named ecosystem — DeepSeek Harness (Cordis), OpenCode v1, OpenCode v2, Goose
   extensions, the Model Context Protocol, VS Code extensions, and the public OpenAI, Anthropic
   and Cursor extension surfaces — what are the documented extension unit, discovery mechanism,
   lifecycle, permission surface, capability declaration, and contribution points, and which of
   those are `unknown` because only marketing or partial source is public?
2. Which ecosystems share a common shape (declared manifest plus typed contribution points plus
   negotiated permissions) and which require host-specific glue that cannot be expressed
   portably, and what evidence supports that classification?
3. What is the documented version-negotiation and compatibility story per ecosystem (schema
   epoch, host API version, deprecation policy), and where is the honest `unknown`?

### Proposed plugin manifest and capability contract

4. What is a minimal Recursion plugin manifest that is expressive enough for the named
   ecosystems yet small enough to be mechanically translatable, covering identity, schema epoch,
   declared contributions, required capabilities, granted capabilities, authority attenuation,
   privacy classification, budget and egress bounds, and evidence/output contract?
5. What should a capability graph be — nodes, edges, attenuation rules, conflict and precedence
   rules — such that a plugin can request exactly the capabilities it needs and no more, and so
   that a plugin's grant can never widen GoalSpec authority, privacy, egress, credential
   visibility, billing or publication?
6. Which parts of the contract must be normative and frozen early (so porters can target it) and
   which parts are adapter-local and must not leak into the canonical contract?
7. How does the contract represent a disabled plugin so that its absence is inert — no process,
   no network, no host mutation, no secret access, no ambient authority — and what evidence
   demonstrates inertness rather than asserting it?

### Porting-cost model

8. What is a defensible porting-cost model (for example per-ecosystem estimated effort bands,
   glue-LOC, adapter surface count, capability-translation steps, conformance failures), and what
   denominators and uncertainty ranges make it falsifiable rather than rhetorical?
9. What is the cheapest credible porting path for each named ecosystem under the proposed
   contract, and what is the competing option (native rewrite, shim, or no port)?
10. Which porting economies are real (shared manifest, shared contribution taxonomy, generated
    adapters) and which are speculative, and what would falsify each claim?

### Falsifiable conformance test design

11. What is a provider-free, deterministic conformance suite that ports the same synthetic plugin
    fixture across the named ecosystems and checks manifest translation, capability attenuation,
    disabled-path inertness, refusal taxonomy and evidence-contract conformance?
12. What are the pass/fail oracles and stop conditions, and what competing option and decisive
    falsifier accompany the proposed contract?

## Deliverable

A source-pinned report containing: a comparison matrix of the named extension models whose every
cell is source-documented, inferred, or `unknown`; a proposed Recursion plugin manifest and
capability-graph contract with normative versus adapter-local boundaries; a porting-cost model
with denominators, ranges and falsifiers; disabled-path inertness requirements stated as
checkable properties; and a falsifiable, provider-free conformance-test design. Each
recommendation names at least one competing option, a decisive falsifier and what it does not
prove. No language, store, framework or vendor is selected.

## Non-goals

- No selection of a language, package manager, sandbox, plugin runtime, store or vendor.
- No installer executed, no plugin loaded, no network effect, no credential handled.
- No claim that any upstream harness or extension ecosystem is certified, stable or CVE-free.
- No implementation of a Recursion loader or capability engine.
- No legal conclusion about licenses or distribution (that belongs to R-C and counsel).
- No reopening of D-018 through D-027.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Each named ecosystem is described from public sources with its extension unit, discovery,
  lifecycle, permissions and contribution points, or explicitly marked `unknown`.
- The proposed manifest and capability contract cover identity, schema epoch, contributions,
  capability request/grant, attenuation, privacy, budget, egress and evidence contract.
- Capability attenuation is stated so no plugin grant can widen a constitutional boundary.
- Disabled-path inertness is stated as checkable properties with an evidence method.
- The porting-cost model carries denominators, uncertainty ranges and a decisive falsifier per
  claim.
- The conformance-test design is provider-free, deterministic, and has explicit oracles and stop
  conditions.
- Every recommendation names a competing option and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.
