---
title: R-P — Prompt injection and untrusted-input defense
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-P — Prompt injection and untrusted-input defense

This is an untrusted-input and prompt-injection handoff for accepted Owner decisions D-018,
D-019, D-022, D-024 and D-031, with the capability and refusal semantics those decisions require
and the gap register in [GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-E](R-E-trusted-launch-boundary.md), the trusted-launch-boundary handoff, and on
[R-U](R-U-sandbox-runtime-isolation-and-supply-chain.md), the sandbox-runtime-isolation and
supply-chain handoff: R-E separates Recursion from the user's credential store and R-U bounds the
execution boundary where untrusted code runs, while R-P designs the defense for the untrusted
*content* that flows into model context, memory, evidence and the effect path. It must extend, not
restate, the capability/grant/attenuation/refusal/accounting semantics those lanes share, and it
feeds [R-Q](R-Q-durable-memory-and-knowledge-architecture.md) and
[R-T](R-T-multimodal-io-and-attachments.md), whose stored and ingested content is untrusted by
default. It does not select a language, store, framework, filter, classifier, runtime or vendor,
does not qualify any route, and executes no provider call.

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

- The object of study is the **input trust boundary**: every byte that reaches model context or
  the effect path from a party Recursion does not itself authoritatively control — web pages,
  repository files, issue and commit text, tool and MCP responses, delegated upstream-harness
  output, other agents' messages, and user-pasted or imported documents and attachments.
- D-018 makes Recursion a first-class native harness *and* a first-class unifying wrapper over the
  wider harness ecosystem; a wrapper that reads foreign harness output and drives foreign CLIs
  necessarily ingests hostile or merely untrusted text. The defense must therefore be
  broker-neutral and route-neutral, not tied to one vendor's guardrail or one model's alignment.
- D-019 ships every capability as an **opt-in plugin or profile** rather than a default. Detection
  or filtering plugins that are disabled must be inert: zero classification call, zero model call,
  zero network egress, zero context mutation and zero stored artifact, not merely a hidden UI.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain` — across configuration, the formal model and the broker. An injected
  instruction must never be able to defeat, forge or suppress a Stop, and the honest boundary
  between "asked to stop" and "observed stopped" must hold on the effect path even while hostile
  content is in context.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. An injected instruction must not become
  authority by surviving compaction, a summary, a memory write or a peer message; provenance and
  the distinction between quoted data and operative instruction must survive every transformation.
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: injection incidents,
  detection rates and refusal outcomes are reported as measured facts, never as vendor-intent
  narratives.
- Non-negotiable direction this lane must respect: authority is a typed capability grant admitted
  by the kernel, not a property of text position; **all model output is an untrusted proposal**;
  effect gating happens at the admitted boundary, not in a vendor hook; a missing counter is
  `unknown`, never zero; and every recommendation carries a competing option, a decisive falsifier
  and an explicit non-proof.
- Prior comparison coverage to extend, not reinvent: the authority model of DS-02, the plugin-trust
  axes of DS-04, the credential/egress broker of DS-24, the exact-action pre-effect mediation
  contract of DS-32 (hooks supply evidence, not receipts), the effect-settlement and receipt
  semantics of M1B, the sandbox boundary of R-U and the trusted-launch boundary of R-E. The
  [ARCHITECTURE-COVERAGE.md](../../research-lane/ARCHITECTURE-COVERAGE.md) edge map records
  untrusted input and prompt injection as an unowned gap, and this handoff is the research that
  reduces it.
- Evidence status: no injection corpus, taint tracker, classifier, refusal fixture or red-team run
  has been implemented or measured by Recursion for this lane. Every detection, prevention,
  false-positive, false-negative, latency and containment statement below is to be established
  from public source, documented behavior and a synthetic provider-free fixture, or marked
  `unknown`.

## Purpose

Produce the decision-ready **prompt-injection and untrusted-input defense design candidate** for
Recursion. The lane specifies the threat model for direct, indirect and cross-agent injection;
taint and provenance tracking for every content unit; instruction-versus-data separation that does
not depend on position or formatting; the rule that all model output is an untrusted proposal;
capability confinement of any party that consumes untrusted content; effect gating at the kernel's
admitted boundary rather than in upstream hooks; a fail-closed refusal and quarantine posture; the
distinction between detection and prevention with honest limits; and provider-free injection test
corpora and red-team fixtures with exact pass/fail predicates. It delivers a design candidate with
competing options, decisive falsifiers and an explicit statement of what it does not prove. It
does not select a language, store, framework, filter, classifier, model, runtime or vendor, does
not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, filter, classifier, guardrail
product, model or vendor.** Do not decide an Owner question recorded in D-018, D-019, D-022, D-024
or D-031. Treat every named external guardrail, classifier or product as prior art cited from
public documentation, not as an endorsed or selected component. No provider, model or account call
is made; no live injection is fired at a real system; no credential or account is touched. Do not
claim that any detector, separator or filter is injection-proof — detection is probabilistic and
prevention is a bounded claim, each with a falsifier. Do not claim that a signature, publisher,
file origin, cache hit or capability *name* confers authority. Do not assert a measured detection
or prevention rate that was not measured; record it `unknown`. Hidden chain-of-thought is neither
requested nor displayed.

## Inputs to read

None from this repository: the rescope, the authority and pre-effect-mediation semantics, the
sandbox and trusted-launch boundaries and the platform floors are summarized in `## Baked context`
above, and no repository, connector or private-source access is assumed. The session must,
however, retrieve the public documentation it cites — the public literature and vendor
documentation on indirect prompt injection, data/instruction separation and tool-result
laundering; the OWASP-style prompt-injection and LLM-application threat guidance; the Model
Context Protocol security guidance for tool and resource trust; public red-team and evaluation
corpora and benchmarks for injection and jailbreak resistance; the public documentation for
content-provenance and data-classification approaches it compares; and the accepted sandbox,
credential and pre-effect-mediation contracts summarized above — and pin each claim to a URL and
retrieval date.

## Research questions

### Threat model, provenance and taint

1. What is the threat model for untrusted input across every ingress: direct user input, retrieved
   web and repository content, tool and MCP results, delegated upstream-harness output, another
   agent's message, and a stored memory or summary that was itself derived from untrusted input —
   and what capability or effect each injection class is trying to reach?
2. What taint and provenance discipline labels each content unit with its origin, trust class,
   retrieval time, deriving transformation chain and the authority it may never carry, so that a
   quotation, summary, translation or re-encoding cannot launder untrusted content into trusted
   content?
3. How are instruction and data separated without relying on position, delimiters, role tags or
   "system" framing that a hostile string can forge, and what structural marker (out-of-band
   metadata, typed content envelope, capability-scoped reference) makes the separation robust to
   compaction, concatenation and provider-specific templating?
4. How is **all model output treated as an untrusted proposal** — including output from the
   orchestrator's own models and from a "trusted" upstream harness — such that no model output can
   widen its own authority, admit a new capability, approve its own action or promote a stored fact
   to an instruction?
5. How do taint labels survive the context pipeline — compaction, summarization, caching, memory
   write, fork and cross-harness handoff — and what is the honest disposition when a transformation
   cannot preserve provenance (fail closed, quarantine, mark `unknown`)?

### Capability confinement and effect gating

6. What capability confinement bounds a party that consumes untrusted content, so that even a
   successful injection cannot exceed the attenuated capability grant the consuming task already
   held, and how is the confinement expressed in the same typed vocabulary as R-U and DS-02?
7. How are instructions that originate in untrusted content prevented from triggering effects by
   being gated at the kernel's **admitted boundary** rather than in an upstream vendor hook, where
   a hook supplies evidence but never a receipt (DS-32), and what negative trace proves a blocked
   effect never reached the irreversible boundary?
8. What is the fail-closed refusal contract — which actions are refused, which are flagged for
   human review, which are quarantined with `paused_with_ambiguity`, and which are allowed because
   they are provably read-only — and how is the refusal reason reported rather than silently
   degraded?
9. How does the defense interact with the D-022 Stop vocabulary: can hostile content in context
   delay, supersede or forge a `checkpoint`, `interrupt` or `drain`, and how is "asked to stop"
   kept distinct from "observed stopped" while tainted content is still being processed?
10. How is a suspicious retrieval or tool result quarantined so it cannot block the canonical
    writer, Stop or recovery, and what is the honest boundary between a heuristic score, a
    confirmed incident and an `unknown`?

### Detection, prevention and their limits

11. What is the precise distinction between **detection** (classify or score untrusted content) and
    **prevention** (structurally deny the path from content to capability), and which layer owns
    which, given that prevention via confinement is the harder guarantee and detection is
    probabilistic?
12. Which defense is appropriate for which injection vector — delimiters, output filtering,
    provenance envelopes, dual-model review, least-privilege tool scoping, human confirmation,
    content sanitization, or effect gating — and what is the competing option and decisive
    falsifier for each?
13. How are false negatives and false positives measured and reported, what harm does each cause
    (a missed injection versus a blocked benign task), and what threshold, if any, could justify
    enabling a detection plugin by default or must remain `unknown` pending measurement?
14. What are the honest limits of the defense: what it cannot detect, what a determined adaptive
    adversary can bypass, what it does not prove about model alignment, and why no claim of
    "injection-proof" is admissible?

### Injection corpora and red-team fixtures

15. What provider-free injection test corpora must accept or reject — direct instruction override,
    indirect injection through a web document, repository file, tool result, MCP resource, peer
    agent message, stored memory, and chained cross-agent injection — with an exact pass/fail
    predicate per case?
16. What evasion and obfuscation cases must the corpus include — unicode and homoglyph tricks,
    encoding and escaping, translation, base64 or nested payloads, role-tag forgery, multi-turn
    gradual escalation, context-window flooding, and tool-result laundering — and how is each
    scored?
17. How do the fixtures prove that a disabled detection plugin is inert (zero call, zero egress,
    zero mutation), that a successful injection cannot widen authority or reach the effect
    boundary, that a refusal is fail-closed and reported, and that taint survives compaction —
    using synthetic content only, with no provider call and no live target?
18. How is each result classified as source-documented, locally observed, inferred or `unknown`,
    and what does the corpus not establish — for example no coverage of an adaptive adversary, no
    measured real-world detection rate and no claim about a specific model or provider?

## Deliverable

A prompt-injection and untrusted-input defense design candidate containing: a threat-model and
provenance section covering every ingress, taint tracking, structural instruction/data separation,
model output as an untrusted proposal and provenance survival across compaction; a
confinement-and-effect-gating section defining capability confinement of untrusted-content
consumers, gating at the kernel's admitted boundary rather than in hooks, the fail-closed refusal
and quarantine contract, and the interaction with the D-022 Stop vocabulary; a
detection-versus-prevention section that separates structural confinement from probabilistic
detection, compares named defenses with a competing option and decisive falsifier each, and states
the honest limits; and a provider-free injection-corpus and red-team-fixture suite for direct,
indirect, cross-agent, obfuscated and multi-turn cases with exact pass/fail predicates. Each
recommendation names a competing option, a decisive falsifier and what it does not prove. No
language, store, framework, filter, classifier, guardrail product, model or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, filter,
  classifier, guardrail product, model or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that any detector, separator, sanitizer or model is injection-proof, or that a
  signature, publisher, file origin or capability name confers authority; each is a bounded or
  `unknown` claim with a falsifier.
- No claim of a measured detection or prevention rate, false-positive rate or coverage where no
  measurement exists; those cells stay `unknown`.
- No provider, model, credential or account call; no live injection, jailbreak or red-team action
  fired at a real system; every fixture is synthetic and provider-free.
- No new executive tier, no separate AI "ARM manager", and no defense that silently replaces the
  kernel's authority admission or the D-022 Stop semantics.
- No assertion that prompt injection can be fully solved, and no vendor-sabotage narrative; all
  incident and outcome reporting is a measured fact (D-031).
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no reopening of the trusted-launch
  boundary in D-029 or the platform floors in D-028.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The threat-model and provenance section covers direct, indirect, cross-agent and stored-content
  injection, labels every content unit with origin, trust class and transformation chain, and
  separates instruction from data structurally rather than by position.
- The candidate states and enforces that all model output is an untrusted proposal, and that taint
  and the quoted-versus-operative distinction survive compaction, summarization, memory write and
  cross-harness handoff with a fail-closed disposition when provenance cannot be preserved.
- The confinement section bounds untrusted-content consumers by the attenuated capability grant,
  gates effects at the kernel's admitted boundary rather than in a vendor hook, and specifies the
  fail-closed refusal and quarantine contract with reported reasons.
- The D-022 interaction is explicit: hostile content cannot forge, delay or suppress a
  `checkpoint`, `interrupt` or `drain`, and "asked to stop" stays distinct from "observed stopped".
- The detection-versus-prevention section distinguishes structural prevention from probabilistic
  detection, gives each named defense a competing option and a decisive falsifier, and states the
  honest limits including why no "injection-proof" claim is admissible.
- The provider-free fixture suite specifies pass/fail predicates for direct, indirect, cross-agent,
  obfuscated and multi-turn injection cases; the disabled-plugin inertness case; the
  authority-widening and effect-boundary negative traces; and the compaction taint-survival case;
  and no fixture requires a provider call or live target.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, filter, classifier, guardrail product, model or vendor is
  selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured detection or prevention
  rate, no coverage of an adaptive adversary, no model-alignment proof, no route qualification and
  no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.
