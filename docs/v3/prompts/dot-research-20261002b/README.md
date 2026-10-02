---
title: Dot research packet — 2026-10-02b
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: each handoff is self-contained; supplying the document launches its session
---

# Dot research packet — 2026-10-02b

This directory holds twenty-one self-contained Deep Research handoffs that extend the 2026-10-02
rescope with the accepted Owner decisions D-018 through D-033. They harden the operating mode
that D-021, D-029 and D-030 opened: Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses, and it must make that delegation real
without ever holding, reading or relaying provider credentials. The decisions served are D-029
(operator-provisioned trusted launch boundary), D-030 (harness-native driving plus headless
fan-out), D-033 (porting is a hypothesis to be validated), D-028 (platform floors), D-031
(no vendor-sabotage claim), D-022 (one pause/stop vocabulary), and, for the source study, D-018
(no ecosystem lock-in), D-019 (build comprehensively, ship lean), D-023 (Codex first, other
harnesses as plugins) and D-024 (productive continuity). The terminal multi-agent lane serves
D-018, D-019, D-022, D-023, D-024 and D-031, with D-021 and D-033 as constraints. The terminal multiplexer and
transformative-TUI lane serves D-018, D-019, D-022 and D-024, with D-021 and D-033 as
constraints. The unified interface platform, graphical-client and backend-performance lanes serve
D-018, D-019, D-022, D-024 and D-031, with D-021 and D-033 as constraints. The Claude Code
terminal-modding study serves D-018, D-019, D-022, D-024 and D-031, with D-021 and D-033 as
constraints and D-033's porting hypothesis as its central question.

Supplying one document is its invocation; run one handoff per sitting. None selects a language,
store, framework or vendor — every recommendation stays evidence for an Owner decision. These
handoffs keep the evidence classes distinct and use public or synthetic sources only.

## Index

| Prompt | Domain | Owner decisions served | Title |
|---|---|---|---|
| [R-E](R-E-trusted-launch-boundary.md) | Trusted launch boundary | D-021, D-028, D-029 | Operator-provisioned trusted launch boundary for strong credential non-intermediation |
| [R-F](R-F-headless-delegation-and-fanout.md) | Headless delegation and fan-out | D-022, D-030 | Harness-native headless delegation and high-volume fan-out |
| [R-G](R-G-plugin-import-and-cross-harness-reuse.md) | Plugin import and reuse | D-019, D-026, D-033 | Importing existing plugin ecosystems and cross-harness plugin reuse |
| [R-H](R-H-counsel-operating-mode.md) | Counsel operating mode | D-021, D-027, D-030, D-031 | Counsel-ready packet for the caller-of-the-CLI operating mode |
| [R-I](R-I-grok-build-source-study.md) | Open-source harness source study | D-018, D-019, D-023, D-024, D-033 | Open-source Grok Build source study: learn, adopt, port or avoid |
| [R-J](R-J-multi-agent-terminal-communication.md) | Terminal multi-agent communication | D-018, D-019, D-022, D-023, D-024, D-031 | Terminal multi-agent communication and parallel-tab experience |
| [R-K](R-K-terminal-multiplexer-and-tui.md) | Terminal multiplexer and transformative TUI | D-018, D-019, D-022, D-024 | Terminal multiplexer and transformative TUI |
| [R-L](R-L-interface-platform-cli-tui-gui.md) | Unified interface platform | D-018, D-019, D-022, D-024, D-031 | Unified interface platform: one command-and-query model for CLI, TUI and GUI |
| [R-M](R-M-claude-code-terminal-modding.md) | Upstream terminal-modding study | D-018, D-019, D-022, D-024, D-031 | Claude Code terminal modding: adopt, port or avoid |
| [R-N](R-N-graphical-client-architecture.md) | Graphical client architecture | D-018, D-019, D-022, D-024, D-031 | Graphical client architecture over the same command-and-query model |
| [R-O](R-O-performance-and-configurability-engineering.md) | Backend performance and configurability | D-019, D-022, D-024, D-031 | Backend performance and configurability engineering |
| [R-P](R-P-prompt-injection-and-untrusted-input-defense.md) | Prompt-injection defense | D-018, D-019, D-022, D-024, D-031 | Defense against prompt injection and untrusted input |
| [R-Q](R-Q-durable-memory-and-knowledge-architecture.md) | Durable memory and knowledge | D-018, D-019, D-024, D-031 | Durable memory and knowledge architecture |
| [R-R](R-R-long-horizon-autonomy-and-scheduling.md) | Long-horizon autonomy | D-018, D-019, D-022, D-024, D-025 | Long-horizon autonomy and scheduling without a standing executive |
| [R-S](R-S-adaptive-optimization-and-outcome-learning.md) | Adaptive optimization | D-019, D-024, D-031 | Adaptive optimization and outcome-driven learning |
| [R-T](R-T-multimodal-io-and-attachments.md) | Multimodal I/O | D-018, D-019, D-024 | Multimodal inputs, outputs and attachments |
| [R-U](R-U-sandbox-runtime-isolation-and-supply-chain.md) | Sandbox runtime and supply chain | D-019, D-021, D-024 | Sandbox runtime, isolation and supply chain |
| [R-V](R-V-observability-introspection-and-replay-debugging.md) | Observability and introspection | D-024, D-031 | Observability, introspection and replay debugging |
| [R-W](R-W-harness-evaluation-and-benchmark-science.md) | Harness evaluation science | D-024, D-031 | Harness evaluation and benchmark science |
| [R-X](R-X-node-fabric-and-remote-execution-protocol.md) | Node fabric and remote execution | D-018, D-019, D-020, D-024 | Node fabric and remote execution protocol |
| [R-Y](R-Y-workspace-and-repository-graph.md) | Workspace and repository graph | D-018, D-019, D-024 | Workspace and repository graph |

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
amendment and never edit a protected path. D-027 authorizes a research packet only: no spend, no
legal commitment and no counsel contact is made by any agent. Public sessions receive only public
or synthetic briefs — never secrets, credentials, personal data, private repository content,
local paths or account/infrastructure identifiers.

The prior evidence these prompts extend is the 2026-10-02 rescope in
[state/DECISIONS.md](../../../../state/DECISIONS.md) (notably D-018, D-019, D-021, D-022, D-023,
D-024, D-026, D-028, D-029, D-030, D-031 and D-033) and the gap register in
[GAPS.md](../../research-lane/GAPS.md).

## Gate

Run from the repository root:

```text
python -X utf8 -B docs/v3/prompts/dot-research-20261002b/check_research_stack.py
```

The check is deterministic and provider-free. It fails unless all twenty-one `R-*.md` files exist, have
the required front matter, contain the research directive and the eight required headings, are
referenced by this README, and have only resolving relative links, with no obvious secret material
and no other-project identifier (reusing `tools.check_public_scope.PATTERN`). A passing check
certifies structure only — not scientific content, source quality or Owner acceptance.
