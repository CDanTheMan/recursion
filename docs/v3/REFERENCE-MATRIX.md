---
title: Recursion v3 evidence-pinned reference and license matrix
status: evidence-grounded
last-updated: 2026-09-03
---

# Recursion v3 evidence-pinned reference and license matrix

## Method

References supply evidence and design alternatives, not authority. The lead resolved each
upstream `HEAD`, opened the cited source or maintainer documentation, and opened its license on
2026-09-03. A branch commit is a dated research pin, not a promise of API stability. Mechanism
descriptions below are scoped to the exact revision.

## Matrix

| Reference and inspected revision | License at revision | Observed mechanism | Adopt/adapt/reject |
|---|---|---|---|
| [T3 Code `5b8445b`](https://github.com/pingdotgg/t3code/tree/5b8445b7a777ab1070aa97b062b1618971073a96) | [MIT](https://github.com/pingdotgg/t3code/blob/5b8445b7a777ab1070aa97b062b1618971073a96/LICENSE) | The [architecture](https://github.com/pingdotgg/t3code/blob/5b8445b7a777ab1070aa97b062b1618971073a96/docs/internals/overview.md) documents one-at-a-time command-queue processing, persisted orchestration command receipts, a pure decider, and event append plus projection in one SQL transaction. It separately names provider and settlement workers, so this is not a single-worker-runtime claim. [Remote identity](https://github.com/pingdotgg/t3code/blob/5b8445b7a777ab1070aa97b062b1618971073a96/docs/internals/remote.md) is server-owned and stable; [resource telemetry](https://github.com/pingdotgg/t3code/blob/5b8445b7a777ab1070aa97b062b1618971073a96/docs/internals/resource-telemetry.md) uses a bounded isolated sidecar. | Adopt command/event/idempotency shape; adapt bounded observers and remote identity. Reject its full UI/runtime stack as v3 core without a measured need. |
| [DeepSeek Harness `76fda72`](https://github.com/deepseek-ai/deepseek-harness/tree/76fda729799fe9b3848dbe2c211d4b231032b81e) | [MIT](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/LICENSE) | [Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/architecture.md) composes typed reversible Cordis capabilities. The [session log](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/subsystems/session.md) is logically append-only and replay-derived; [persistence](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/subsystems/persistence.md) may be write-behind, with resolved `flush` as the crash-survival barrier. [Compaction](https://github.com/deepseek-ai/deepseek-harness/blob/76fda729799fe9b3848dbe2c211d4b231032b81e/docs/subsystems/compaction.md) records start/summary/end and makes interrupted work detectable. | Adopt durable-versus-live event distinction and compaction transaction markers. Adapt plugin composition behind a non-replaceable authority kernel and define Recursion's own durability barrier. |
| [Hermes Agent `bd6cc48`](https://github.com/NousResearch/hermes-agent/tree/bd6cc48b94f752d0e0977bf4050fa678e18b714e) | [MIT](https://github.com/NousResearch/hermes-agent/blob/bd6cc48b94f752d0e0977bf4050fa678e18b714e/LICENSE) | The [README](https://github.com/NousResearch/hermes-agent/blob/bd6cc48b94f752d0e0977bf4050fa678e18b714e/README.md) documents multi-provider models, gateway channels, delegation, terminal backends, skills, cron and compression. Source-level state claims were not completed in this campaign. | Retain/audit the existing downstream seam and reuse proven integrations. Treat README behavior as documented interface, not proof of durable Head/ARM semantics. |
| [Pi `4e69b0c`](https://github.com/earendil-works/pi/tree/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057) | [MIT](https://github.com/earendil-works/pi/blob/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057/LICENSE) | [Agent core](https://github.com/earendil-works/pi/blob/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057/packages/agent/README.md) separates model conversion, turn/tool events and execution modes and exposes an awaited `beforeToolCall` veto in its higher-level API; [AI core](https://github.com/earendil-works/pi/blob/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057/packages/ai/README.md) owns provider/model streaming; [SQLite sessions](https://github.com/earendil-works/pi/blob/4e69b0c28060f0f02fbe38bfa7c21a2e2eb25057/packages/session-backends/sqlite-node/README.md) are optional, not forced into core. | Adopt the provider/loop split and optional backend discipline. Adapt its policy hooks inside Recursion's authoritative budget, sandbox and publication boundary; the hooks alone are insufficient for unattended authority. |
| [Claude Code `f173a69`](https://github.com/anthropics/claude-code/tree/f173a697aa6486945f1b9c4aa9ce5383d2c87db6) | [Proprietary Commercial Terms](https://github.com/anthropics/claude-code/blob/f173a697aa6486945f1b9c4aa9ce5383d2c87db6/LICENSE.md) | The public repository exposes [plugin examples and structure](https://github.com/anthropics/claude-code/blob/f173a697aa6486945f1b9c4aa9ce5383d2c87db6/plugins/README.md), not the complete CLI implementation. | Behavioral/interface reference only. Do not infer CLI internals or copy proprietary implementation. |
| [OpenCode `b578b72`](https://github.com/anomalyco/opencode/tree/b578b7261fc9ec4917fe272df5cc4bd8a056cd5d) | [MIT](https://github.com/anomalyco/opencode/blob/b578b7261fc9ec4917fe272df5cc4bd8a056cd5d/LICENSE) | The pinned plugin [index](https://github.com/anomalyco/opencode/blob/b578b7261fc9ec4917fe272df5cc4bd8a056cd5d/packages/opencode/src/plugin/index.ts) applies resolved plugins and generic hooks sequentially, resolves configured external origins in parallel, and fires event hooks without awaiting them. Pure mode suppresses configured external origins but retains internal plugins. The GitHub API reports `anomalyco/opencode` is not a fork; `sst/opencode` and `anomalyco/opencode` resolved to the same HEAD on 2026-09-03. | Adapt hook vocabulary and only the ordering semantics proven for each hook path, behind stronger integrity and isolation. Do not treat pure mode or in-process plugins as a sandbox. |
| [Gemini CLI `55b495d`](https://github.com/google-gemini/gemini-cli/tree/55b495d6db1794bf5b7f37a9bc03ebcab5103673) | [Apache-2.0](https://github.com/google-gemini/gemini-cli/blob/55b495d6db1794bf5b7f37a9bc03ebcab5103673/LICENSE) | The pinned [tool reference](https://github.com/google-gemini/gemini-cli/blob/55b495d6db1794bf5b7f37a9bc03ebcab5103673/docs/reference/tools.md) documents policy checks, confirmation, trusted folders, sandboxing, tool discovery and a plan mode. | Optional engine reference. Recursion still supplies non-interactive authority, budget, evidence and publication gates around it. |
| [Cursor CLI docs, opened 2026-09-03](https://prod.cursor.com/docs/cli/overview) | Proprietary documentation/interface | The direct official CLI page documents interactive and non-interactive modes plus resumable sessions. A Muse review correctly found that the generic `cursor.com/docs` index alone did not expose those details; the lead then opened this direct page. This campaign did not inspect a full open-source CLI implementation or prove any account/model entitlement. | Optional engine/interface reference only; retain fake-transport and exact-assignment verification in Recursion. |
| [Codex subagents, opened 2026-09-03](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Documentation terms | Official docs describe explicit per-subagent model/reasoning overrides and a configured concurrency ceiling. | Construction route evidence only; do not hard-code this app's swarm mechanics into v3. |
| [OpenAI compaction, opened 2026-09-03](https://developers.openai.com/api/docs/guides/compaction) | Documentation terms | Native compaction may return an opaque encrypted item carrying prior state; it is not a human-inspectable portable Recursion record. | Preserve provider affinity where useful; require local intent/evidence fidelity and portable capsules independently. |
| [OpenCode Go, opened 2026-09-03](https://dev.opencode.ai/docs/go/) | Documentation terms | Official docs list the exact Contributor model, usage limits and training/retention caveat; model list and limits are explicitly changeable. | Route capability evidence only. Contributor traffic stays public/synthetic and never becomes entitlement or billing proof. |

## Cross-reference questions

### Executive architecture

- Which systems distinguish a durable logical actor from the model serving it?
- How are parent/child sessions represented, resumed, cancelled, and budgeted?
- Which delegation trees survive process death, and which are only in-memory conveniences?
- What can Recursion retain from Hermes without coupling the v3 kernel to one provider loop?

### Context and cache

- Who owns active compaction on each route?
- What exact fields, hooks, session IDs, cache counters, and thresholds are observable?
- How do systems prevent repeated summary-of-summary drift?
- Which context layouts preserve provider prefix-cache affinity?
- What evidence supports claimed token savings or recall quality?

### Plugins

- How are plugin dependencies, exclusive capabilities, event ordering, isolation, and disposal handled?
- Which extension mechanisms mutate shared globals or monkey-patch internals?
- What is the idle/startup cost of discovery and loading?
- Which licenses and attribution obligations apply to code reuse?

### State and recovery

- Which events are durable and transactionally projected?
- How are side effects reconciled after ambiguous failure?
- How do worktree/session snapshots interact with non-Git state?
- Which schema/migration techniques can support v2 import without dual-write truth?

### Operator experience

- How do CLI tools expose provider auth, models, permissions, configuration precedence, and diagnostics?
- Which commands are stable and machine-readable enough for an Observer Interface?
- How do products warn about dangerous modes without blocking owner choice?
- What is genuinely required at startup versus relegated to explicit conformance/doctor commands?

## Differentiation hypothesis

No inspected reference directly demonstrated this complete lineage:

```text
owner intent -> versioned goal -> Head -> ARM -> delegated segment
-> explained route/capacity pool -> provider session -> checkpoint/diff
-> independent evidence -> review publication -> quality/quota/cache outcome
```

This is a comparative inference, not proof of uniqueness. It becomes meaningful only if
identifiers drive admission, recovery, budget enforcement, context selection, verification
and route learning—not if they are decorative log fields. Revalidate on reference revision
changes and before any public differentiation claim.

## Source-quality limits

- Repository documentation and source prove only the pinned revision, not deployment or future
  behavior.
- Marketing/README claims are labeled documented behavior unless implementation was opened.
- MIT compatibility permits reuse subject to notice requirements; it does not make a design a
  good fit. The Claude Code material is not a reusable source base under this review.
- The `anomalyco/opencode` repository is not marked as a GitHub fork; the legacy `sst/opencode` URL resolved to the same HEAD on 2026-09-03. Revalidate repository identity on future revision changes rather than assuming either divergence or parity.
- Stars, forks and estimated request counts were rejected as architecture or maintenance
  evidence.
- Provider pricing, limits, privacy and model availability expire on documentation or local
  route change; see [ROUTE-CAPABILITIES.md](ROUTE-CAPABILITIES.md).
