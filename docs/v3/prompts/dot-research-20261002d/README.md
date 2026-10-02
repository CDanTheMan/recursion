---
title: Dot research packet — 2026-10-02d (scales-with-your-workflow composition)
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Dot research packet — 2026-10-02d (scales-with-your-workflow composition)

This directory holds three self-contained Deep Research handoffs that extend the accepted
2026-10-02 product thesis D-034 — **"Recursion — the harness that scales with your workflow"** —
and make its two load-bearing claims falsifiable: that the effective system prompt/context is
**deterministically composed** from the installed capability set plus the GoalSpec, and that
"scales" is **measurable at a fixed budget** rather than "more is always better." The packet also
carries the composition thesis into the two client surfaces D-034 names as optional client
plugins: a typed UI projection contract, and iOS/Android control-surface clients over a
remote-capable backend.

All three handoffs serve D-034 and the decisions it depends on: D-018 (no ecosystem lock-in),
D-019 (build comprehensively, ship lean, opt-in install), D-022 (one pause/stop vocabulary —
Aggressive/Full/Lazy plus `checkpoint`/`interrupt`/`drain`), D-024 (productive continuity),
D-031 (no vendor-sabotage or unmeasured savings claim) and D-034 (the scaling thesis), with D-021
and D-033 as constraints. The prompt/context lane extends the delivered 2026-10-02c
Prompt/Plugin/Skill architecture and the R-Q/R-L/R-O/R-A/R-W lines; the UI lane extends R-L, R-N,
R-K and R-A's capability graph; the mobile lane extends R-L, R-N, R-K, R-X and the accepted
remote-execution fabric.

Supplying one document is its invocation; run one handoff per sitting. None selects a language,
store, framework, UI toolkit, transport, push provider or vendor — every recommendation stays
evidence for an Owner decision. These handoffs keep the evidence classes distinct and use public
or synthetic sources only.

## Index

| Prompt | Domain | Owner decisions served | Title |
|---|---|---|---|
| [R-PC](R-PC-capability-driven-prompt-composition.md) | Capability-driven prompt and context composition | D-018, D-019, D-022, D-024, D-031, D-034 | Capability-driven prompt and context composition |
| [R-UI](R-UI-capability-driven-ui-projection.md) | Capability-driven UI projection | D-018, D-019, D-022, D-024, D-031, D-034 | Capability-driven UI projection contract |
| [R-MOB](R-MOB-mobile-and-remote-control-clients.md) | Mobile and remote-control clients | D-018, D-019, D-022, D-024, D-031, D-034 | Mobile and remote control clients |

The lanes divide as follows. **R-PC** owns the deterministic compiler from the effective
capability set plus GoalSpec to one versioned effective prompt/context artifact, including
determinism and versioning, stable cache prefixes, provenance and `authority_carried_none`
injection safety, conflict/precedence rules, and the fixed-budget scaling experiment. **R-UI**
owns the typed, versioned UI-contribution contract by which any client deterministically
materializes UI from the effective capability set and projections, including fail-closed
unknown-capability refusal, the contribution-point taxonomy, plugin-contributed UI security, and
parity with the ten controls and three Stops. **R-MOB** owns pairing and device authentication,
remote session control, offline read views with "last synchronized" honesty, push/notification
semantics, no credential custody, last-window-close != Stop, and the app-store
distribution/licensing questions that go to counsel under G-32.

## Running a session

Supply the `R-*.md` document to the session. It opens with a research directive that names the
task, authorizes the investigation and forbids asking which topic to research. Nothing else has
to be typed, and the document does not depend on a repository connector — all context is baked
in under `## Baked context`.

## Authority

Each handoff is self-contained: a Deep Research session needs no repository access because the
shared authority, scope, evidence and privacy context is baked into every file. The operator
should read [CONTROL_PLANE.md](../../../../CONTROL_PLANE.md), [ANCHOR.md](../../../../ANCHOR.md)
and [AGENTS.md](../../../../AGENTS.md) before invoking a session.

Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses. Hermes-led control was retired on 2026-09-28 (state/DECISIONS.md D-017); Hermes is an
optional upstream integration, not the executive control plane. These prompts propose no
amendment and never edit a protected path. D-027 authorizes a research packet only: no spend, no
legal commitment and no counsel contact is made by any agent. Public sessions receive only public
or synthetic briefs — never secrets, credentials, personal data, private repository content,
local paths or account/infrastructure identifiers. No language, store, framework, UI toolkit,
transport, push provider or vendor is selected by any handoff.

The prior evidence these prompts extend is the 2026-10-02 rescope in
[state/DECISIONS.md](../../../../state/DECISIONS.md) (notably D-017, D-018, D-019, D-021, D-022,
D-024, D-031 and D-034) and the gap register in
[GAPS.md](../../research-lane/GAPS.md).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/dot-research-20261002d/check_research_stack.py
```

The check is deterministic and provider-free. It fails unless all three `R-*.md` files exist, have
the required front matter, contain the research directive and the eight required headings, are
referenced by this README, and have only resolving relative links, with no obvious secret material
and no other-project identifier (reusing `tools.check_public_scope.PATTERN`). A passing check
certifies structure only — not scientific content, source quality or Owner acceptance.
