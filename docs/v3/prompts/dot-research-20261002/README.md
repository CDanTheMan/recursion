---
title: Dot research packet — 2026-10-02
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Dot research packet — 2026-10-02

This directory holds four self-contained Deep Research handoffs that commission autonomous
research to harden the Recursion product after the 2026-10-02 rescope. That rescope is recorded
in the accepted Owner decisions D-018 through D-027 of [state/DECISIONS.md](../../../../state/DECISIONS.md):
Recursion is both a native harness and a unifying wrapper (D-018); it builds comprehensively and
ships lean, install opt-in (D-019); availability takeover is a plugin over a single-node core
(D-020); it delegates to user-authenticated local tools rather than intermediating credentials
(D-021); Codex App Server is the first qualified upstream profile (D-023); the headline
differentiator is productive continuity (D-024); continuing autonomous research is an optional
bounded plugin (D-025); the project releases under Apache-2.0 to grow a porter community (D-026);
and a counsel-ready packet is authorized with no spend (D-027).

Supplying one document is its invocation; run one handoff per sitting. None selects a language,
store, framework or vendor — every recommendation stays evidence for an Owner decision. These
handoffs keep the evidence classes distinct and use public or synthetic sources only.

## Index

| Prompt | Domain | Owner decisions served | Title |
|---|---|---|---|
| [R-A](R-A-plugin-portability.md) | Plugin portability | D-018, D-019, D-026 | Plugin and capability-graph contract for cheap porting |
| [R-B](R-B-cross-harness-delegation.md) | Cross-harness delegation | D-021, D-023, D-024 | Delegating across harnesses without credential intermediation |
| [R-C](R-C-route-legal-and-licensing.md) | Route legality and licensing | D-021, D-026, D-027 | Per-route terms, credential limits and Recursion's licensing posture |
| [R-D](R-D-quota-efficiency-measurement.md) | Quota efficiency measurement | D-018, D-024 | Falsifiable quota, usage and lock-in measurement |

## Running a session

Supply the `R-*.md` document to the session. It opens with a research directive that names the
task, authorizes the investigation and forbids asking which topic to research. Nothing else has
to be typed, and the document does not depend on a repository connector — all context is baked
in under `## Baked context`.

## Authority

Each handoff is self-contained: a Deep Research session needs no repository access because the
shared authority, scope, evidence and privacy context is baked into every file. The operator
should read [CONTROL_PLANE.md](../../../../CONTROL_PLANE.md), `ANCHOR.md` and `AGENTS.md` before
invoking a session. Hermes-led control was retired on 2026-09-28 (state/DECISIONS.md D-017); these prompts propose no
amendment and never edit a protected path. D-027 authorizes a research packet only: no spend,
no legal commitment and no counsel contact is made by any agent. Public sessions receive only
public or synthetic briefs — never secrets, credentials, personal data, private repository
content, local paths or account/infrastructure identifiers.

The prior evidence these prompts extend is the 2026-10-02 rescope in
[state/DECISIONS.md](../../../../state/DECISIONS.md) and the gap register in
[GAPS.md](../../research-lane/GAPS.md).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/dot-research-20261002/check_research_stack.py
```

The check is deterministic and provider-free. It fails unless all four `R-*.md` files exist, have
the required front matter, contain the research directive and the eight required headings, are
referenced by this README, and have only resolving relative links, with no obvious secret material
and no other-project identifier (reusing `tools.check_public_scope.PATTERN`). A passing check
certifies structure only — not scientific content, source quality or Owner acceptance.
