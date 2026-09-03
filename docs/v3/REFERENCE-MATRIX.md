---
title: Recursion v3 reference-repository matrix
status: preliminary-research
last-updated: 2026-09-02
---

# Recursion v3 reference-repository matrix

## Method

References supply evidence and design alternatives, not authority. The overnight research should pin current revisions, inspect implementation rather than README claims alone, record licenses, and distinguish reusable code from behavioral inspiration. Closed-source systems are behavioral references only unless a clearly compatible licensed artifact exists.

All findings below are preliminary observations from the archived session and must be revalidated before they become normative.

## Matrix

| Reference | Behavior to study | Candidate adoption | Recursion-specific extension | Do not copy blindly |
|---|---|---|---|---|
| [T3 Code](https://github.com/pingdotgg/t3code) | Server-owned workspaces/sessions, typed command/event flow, transactional projections, provider drivers, bounded resource telemetry | One coordinator boundary, deterministic commands/events, lazy provider helpers, stable observer protocol | Add owner authority, goal-scoped ARMs, multi-pool budgets, cross-provider lineage, independent publication evidence | Full UI/server stack or resident monitoring before the personal CLI proves it needs them |
| [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) | Typed services/events, plugin profiles/tree, lifecycle disposal, replaceable agent/compaction capabilities | Capability manifests, deterministic plugin composition, explicit lifecycle, durable versus ephemeral events | Keep authority/PAUSE/budget/publication in a privileged kernel and add resource-discipline contracts | Treating the integrity constitution or canonical writer as an ordinary replaceable plugin |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Agent loop, provider routing, delegation, session storage, compression/caching, skills/tools | Retained upstream base, isolated delegated contexts, provider integrations, proven loop behavior | Durable Head/ARM outer lifecycle, authority inheritance, model-aware pools, evidence/publication, cross-harness continuation | Assuming child sessions or provider fallbacks are durable/authorized merely because the inner loop supports them |
| [Pi](https://github.com/earendil-works/pi) | Minimal core, extensible providers/tools, sessions/branching, compaction extensions, subscription integrations | Minimal runtime instincts, explicit extension seams, provider compatibility data | Add strong permission, budget, node, evidence, and publication enforcement around the minimal loop | Adopting a deliberately light permission model for remote or unattended execution |
| [Claude Code](https://github.com/anthropics/claude-code) | Subagents, hooks, worktrees, permissions, monitoring, compact/summary behavior, plugin packaging | Lifecycle hooks, clean verifier context, risk-scaled permission UX, observable compaction boundaries | Non-lossy Owner Intent, proof-carrying verification, portable capsules, route/budget correlation | Treating generated compaction summaries as lossless or making Claude-specific semantics canonical |
| [OpenCode](https://github.com/anomalyco/opencode) | Primary/subagent roles, client/server API, provider registry, session events, snapshots, output bounding, compaction | Stable server/observer interfaces, hidden maintenance agents, provider-neutral session abstractions | Authority-aware ARM hierarchy, external-effect ledger, subscription capacity pools, review-only publication | Assuming Git snapshots reverse processes, services, databases, or network effects |
| [Cursor](https://cursor.com/blog/self-summarization) | Composer self-summarization, native CLI sessions/subagents, hooks, model pool behavior | Use Cursor as an optional high-throughput engine and respect its active compaction ownership | Context Capability Descriptors, portable sidecar state, cache-domain-aware route stability | Assuming every third-party model routed through Cursor is trained for Cursor's compaction or uses a particular subscription entitlement |
| [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction) | Opaque/native compaction, server-side thresholds, usage accounting, prompt caching | Preserve route-native state and stable prefixes where officially supported | Deterministic fidelity validation, cross-provider capsule, exact local rehydration | Claiming opaque native state is portable or that OAuth CLIs expose every API cache control |
| [ccusage](https://github.com/ccusage/ccusage) | Local read-only parsing of completed agent usage records | Optional reconciliation/calibration evidence provider | Correlate imported usage to Goal/ARM/task/route/evidence with confidence labels | Treating reconstructed history or API-equivalent cost as live subscription capacity truth |

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

## Preliminary differentiation hypothesis

No single reference appears, from the public material reviewed in-session, to connect this complete lineage:

```text
owner intent -> versioned goal -> Head -> ARM -> delegated segment
-> explained route/capacity pool -> provider session -> checkpoint/diff
-> independent evidence -> review publication -> quality/quota/cache outcome
```

The combination could make Recursion distinctive. It becomes meaningful only if identifiers drive admission, recovery, budget enforcement, context selection, verification, and route learning—not if they are decorative log fields.

## Required overnight deliverable

For each reference, record:

- pinned revision/date and license;
- exact source/docs links;
- verified architecture claims;
- reusable interface or pattern;
- difference from Recursion's requirements;
- adoption, adaptation, or rejection recommendation;
- experiment or spike needed;
- resource and maintenance implications.
