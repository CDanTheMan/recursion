---
title: Dot reconciliation packet — 2026-10-02c
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Dot reconciliation packet — 2026-10-02c

This directory holds one self-contained Deep Research handoff. It does not open a new research
front and it selects no technology. It reconciles the **shared contracts** that lanes R-L, R-Q,
R-P, R-T, R-V, R-X and R-Y already proposed to each other, so that the overnight integration
synthesis (`docs/v3/research-lane/overnight-20261002/synthesis/`) is turned into one
accepted-candidate field map plus the decisive vectors that would falsify it. The decision served
is the identity, content, receipt, publication-ordering and resource-conservation spine that every
other Recursion v3 contract depends on.

Supplying the document is its invocation; run the handoff in one sitting. It selects no language,
store, framework, runtime, transport, encoding, schema or vendor — every recommendation remains
evidence for an Owner decision. It keeps evidence classes distinct and uses public or synthetic
sources only.

## Index

| Prompt | Domain | Owner decisions served | Title |
|---|---|---|---|
| [R-SC](R-SC-shared-contract-reconciliation.md) | Shared contract reconciliation | D-018, D-019, D-022, D-024, D-031 | Shared contract reconciliation across the mutually delegated lanes |

## Running a session

Supply the `R-*.md` document to the session. It opens with a research directive that names the
task, authorizes the investigation and forbids asking which topic to research. Nothing else has
to be typed, and the document does not depend on a repository connector — all context is baked
in under `## Baked context`.

## Authority

Each handoff is self-contained: a Deep Research session needs no repository access because the
shared authority, scope, evidence and privacy context is baked into every file. The operator
should read [CONTROL_PLANE.md](../../../../CONTROL_PLANE.md), [ANCHOR.md](../../../../ANCHOR.md)
and `AGENTS.md` before invoking a session.

Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses. Hermes-led control was retired on 2026-09-28 (state/DECISIONS.md D-017); Hermes is an
optional upstream integration, not the executive control plane. These prompts propose no
amendment and never edit a protected path. Public sessions receive only public or synthetic
briefs — never secrets, credentials, personal data, private repository content, local paths or
account/infrastructure identifiers.

The prior evidence this prompt extends is the 2026-10-02 rescope in
[state/DECISIONS.md](../../../../state/DECISIONS.md) (notably D-018, D-019, D-022, D-024 and
D-031), the lane reports in `docs/v3/research-lane/overnight-20261002/`, and the integration
synthesis (`OWNERSHIP-AND-FIELD-MAP.md`, `MODEL-ARCHITECTURE.md`,
`INTEGRATION-TEST-HANDOFF.md`).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/dot-reconciliation-20261002c/check_research_stack.py
```

The check is deterministic and provider-free. It fails unless
`R-SC-shared-contract-reconciliation.md` exists, has the required front matter, contains the
research directive and the eight required headings, is referenced by this README, and has only
resolving relative links, with no obvious secret material and no other-project identifier
(reusing `tools.check_public_scope.PATTERN`). A passing check certifies structure only — not
scientific content, source quality or Owner acceptance.
