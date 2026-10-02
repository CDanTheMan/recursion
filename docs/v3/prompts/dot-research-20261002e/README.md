---
title: Dot research packet — 2026-10-02e (core language + control-surface study)
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Dot research packet — 2026-10-02e (core language + control-surface study)

This directory holds **two** self-contained Deep Research handoffs that run in parallel with local
construction work. They serve the accepted thesis D-034 — **"Recursion — the harness that scales
with your workflow"** — together with D-018 (no ecosystem lock-in), D-023 (Codex App Server is the
first qualification priority), D-028 (platform floors), D-030 (harness-native driving plus headless
fan-out), D-031 (no vendor-sabotage or unmeasured-savings claim), D-033 (porting is a hypothesis),
D-035 (plugins live outside the core) and D-039 (accept the OS/language advisory and plan a
language-agnostic architecture).

Neither handoff selects a language, store, framework, UI toolkit, transport, push provider, license
or vendor; every recommendation stays evidence for an Owner decision.

- **R-LANG** fills the gap the mobile-only OS/language packet left open: it evaluates candidate
  implementation languages and runtimes for the **core/backend** against the D-028 platform floors,
  the FU-03 deterministic-kernel results and the FU-02 store crash/replay questions, and it defines
  how to specify the architecture **language-agnostically** so a later language change is a bounded
  reconstruction rather than a re-derivation (the D-039 falsifier).
- **R-CS** is a systematic, evidence-classed study of **agent-harness control surfaces and
  orchestrators** — anchored on T3 Code (v0.0.45) and its peers — covering architecture, plugin and
  skill lifecycle, continuity and notification semantics, quota-by-credential, mobile stack choices
  and licensing, so Recursion's differentiation on D-034 stays honest.

Supplying one document is its invocation; run one handoff per sitting. These handoffs keep the
evidence classes distinct and use public or synthetic sources only.

## Index

| Prompt | Domain | Owner decisions served | Title |
|---|---|---|---|
| [R-LANG](R-LANG-core-language-and-architecture-reconstruction.md) | Core/backend language, runtime and language-agnostic architecture | D-018, D-028, D-033, D-034, D-035, D-039 | Core language, runtime and architecture reconstruction |
| [R-CS](R-CS-control-surface-and-competitor-study.md) | Agent-harness control surfaces and competitor study | D-018, D-023, D-030, D-031, D-034, D-035 | Control-surface and competitor study |

The lanes divide as follows. **R-LANG** owns the candidate-language/runtime evaluation for the
deterministic core and backend against the platform floors and the FU-01/FU-02/FU-03 results, the
plugin-host/FFI/WASM boundary, and the language-agnostic architecture specification plus its
reconstruction acceptance criteria. **R-CS** owns the control-surface/competitor comparison:
architecture, plugin/skill lifecycle, continuity and notification semantics, quota-by-credential,
mobile stack evidence and licensing — all from public sources, without copying and without
vendor-intent claims.

## Running a session

Supply the `R-*.md` document to the session. It opens with a research directive that names the task,
authorizes the investigation and forbids asking which topic to research. Nothing else has to be
typed, and the document does not depend on a repository connector — all context is baked in under
`## Baked context`.

## Authority

Each handoff is self-contained: a Deep Research session needs no repository access because the
shared authority, scope, evidence and privacy context is baked into every file. The operator should
read [CONTROL_PLANE.md](../../../../CONTROL_PLANE.md), [ANCHOR.md](../../../../ANCHOR.md) and
[AGENTS.md](../../../../AGENTS.md) before invoking a session.

Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses. Hermes-led control was retired on 2026-09-28 (state/DECISIONS.md D-017); Hermes is an
optional upstream integration, not the executive control plane. These prompts propose no amendment
and never edit a protected path. D-027 authorizes a research packet only: no spend, no legal
commitment and no counsel contact is made by any agent. Public sessions receive only public or
synthetic briefs — never secrets, credentials, personal data, private repository content, local
paths or account/infrastructure identifiers. No language, store, framework, UI toolkit, transport,
push provider or vendor is selected by any handoff.

The prior evidence these prompts extend is the 2026-10-02 rescope in
[state/DECISIONS.md](../../../../state/DECISIONS.md) (notably D-018, D-023, D-028, D-031, D-033,
D-035 and D-039), the accepted decisions it builds on, the mobile OS/language advisory intake in
[capability-composition and iOS/Android intakes](../dot-research-20261002d/README.md), and the gap
register in [GAPS.md](../../research-lane/GAPS.md).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/dot-research-20261002e/check_research_stack.py
```

The check is deterministic and provider-free. It fails unless both `R-*.md` files exist, have the
required front matter, contain the research directive and the eight required headings, are
referenced by this README, and have only resolving relative links, with no obvious secret material
and no other-project identifier (reusing `tools.check_public_scope.PATTERN`). A passing check
certifies structure only — not scientific content, source quality or Owner acceptance.
