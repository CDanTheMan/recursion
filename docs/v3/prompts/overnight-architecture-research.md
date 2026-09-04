---
title: Overnight Codex prompt — ground the Recursion v3 architecture
status: superseded-do-not-run
last-updated: 2026-09-02
superseded-by: ../FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md
---

# Overnight Codex prompt — ground the Recursion v3 architecture

> **Do not run this prompt.** It predates `OWN-FHAR-001`, the proposed Recursion Head identity,
> the planning-contract baseline, and the completed frontier-harness campaign. It remains only as
> provenance; use the active campaign artifacts and a newly authorized bounded prompt instead.

Copy everything below the divider into a new Codex task opened on the local `codex/v3-design-foundation` worktree.

---

You are the lead architecture researcher for a documentation-only Recursion v3 control-plane authoring session explicitly authorized by Lucas.

## Parent goal

Turn the initial Recursion v3 hypothesis into an evidence-grounded architecture package that can safely drive a later large autonomous implementation session. Preserve the ambitious destination: Recursion becomes its own provider-neutral autonomous-development harness and integration system. Do not reduce v3 to a compatibility wrapper around v2. Also do not confuse destination ambition with construction method: the future implementation must remain incremental, reversible, and independently gated.

Quality and truth are more important than speed. Minimize subscription-quota burn: use deterministic repository inspection and primary-source reading before model-heavy synthesis. Do not make activity for the sake of filling the night.

## Exact authority and scope

Allowed writes:

- `docs/v3/**`

Read access:

- the entire Recursion repository;
- Git history and current remote references through non-mutating commands;
- primary official documentation, source repositories, papers, and licenses needed for architectural research.

Explicit non-goals:

- no product/runtime implementation;
- no changes to `CONTROL_PLANE.md`, `ANCHOR.md`, `AGENTS.md`, `state/**`, `scripts/**`, `config/**`, schemas, services, credentials, auth, routing, cron, PAUSE, or environment files;
- no VPS mutation, deployment, restart, unpause, notification, or provider-account change;
- no merge, rebase, reset, branch pruning, force operation, pull request, or publication;
- no `git push` of any kind;
- no metered model/API spending or fallback;
- no access to private project source unless Lucas separately and explicitly grants it in that task;
- do not begin the v3 construction campaign.

You may commit documentation-only checkpoints locally on `codex/v3-design-foundation`. Never publish them. If the branch or allowed-path boundary is not exact, stop before writing and report the mismatch.

## Authority model you must preserve

```text
Lucas — principal
  -> Main Assistant / Head Hermes — portfolio executive
       -> goal-scoped ARM executives — plan, delegate, replan, checkpoint
            -> bounded agents / native or external harness sessions
                 -> machine gates + independent verifier
       -> deterministic Recursion kernel — authority, state, budgets,
          routing, leases, PAUSE, evidence, publication
  -> Lucas reviews, merges, provisions credentials, and deploys
```

Head Hermes directly manages ARMs. There is no separate AI ARM Manager. The kernel enforces actors but does not replace their semantic judgment. Logical actor identity is distinct from model escalation, provider failover, delegation, executive replacement, and authority escalation.

The current `CONTROL_PLANE.md` remains authoritative. If provider-neutral executive routing would require changing its Codex-OAuth planning-model clause, document the exact proposed amendment and conflict; do not edit the constitution.

## Start here

1. Read `CONTROL_PLANE.md`, `ANCHOR.md`, and repository `AGENTS.md` completely.
2. Verify the branch, merge base, worktree status, and allowed paths. Preserve any user-owned changes.
3. Read every file under `docs/v3/`, including the sanitized transcript, decision register, hypotheses, and this prompt.
4. Read the accepted v2 baseline and ancestral architecture, especially:
   - `docs/recursion-v2-mvp-harness.md`
   - `docs/architecture.md`
   - `docs/delegation-design.md`
   - `docs/plans/hermes-project-pilot-production-plan.md`
   - `docs/plans/recursion-v2-execution-fabric.md`
   - `docs/plans/engine-plugin-architecture.md`
   - `docs/plans/remote-execution-adapters.md`
   - relevant v1/v2 schemas, tests, CLI, supervisor, pilot, reconciler, adapter, state, evidence, and publication code.
5. Treat `98113d6c6d3debe2a4d207c51bb1780f7356d714` as the merged v2 source baseline unless Git proves a newer explicit base is intended. Never assume the deployed VPS matches it.

## Use bounded research delegation

Delegate independent read-only lanes when useful, keeping one lead responsible for synthesis and file edits:

1. **Current-system archaeology:** trace Head Hermes, Project Pilots, planning, reconciliation, work dispatch, v2 MVP orchestration, adapters, state stores, gates, publication, and CLI. Produce file/symbol/test evidence and identify duplicate truths.
2. **Reference harnesses:** inspect pinned current revisions and licenses for T3 Code, DeepSeek Harness, Hermes Agent, Pi, Claude Code public materials, and OpenCode. Add Cursor, OpenAI/Codex, Gemini CLI, and `ccusage` only through primary sources. Identify what to adopt, adapt, or reject.
3. **Performance/state/security:** challenge SQLite, plugin, node, context, compaction, credential, egress, and small-VPS assumptions. Design measurable budgets and failure experiments without implementing them.

Subagents do not edit shared docs. They return concise evidence packets with source links, revisions, confidence, contradictions, and open questions. The lead reconciles them. Avoid duplicate broad prompts and unbounded recursive delegation.

## Research questions

### Existing Recursion

- What exact behavior exists versus only being documented or tested?
- How does the operational Head/Pilot hierarchy actually create, monitor, retry, verify, and close work?
- Where does model escalation exist in configuration, code, and tests? Where is it missing?
- What would it take to represent a Project Pilot as a first-class goal-scoped ARM executive?
- Which v2 contracts are reusable unchanged, which require versioned extension, and which are accidental complexity?
- Which files/modules have overlapping responsibilities or state representations?
- Which same-process defenses could be replaced by clearer process/capability boundaries?
- What is the smallest safe migration path from current operational code to one canonical v3 kernel?

### Native harness boundary

- Which agent-loop responsibilities must Recursion own to be an independent harness?
- Which should remain in Hermes or external CLIs to preserve provider-tuned tool use, delegation, and compaction?
- Should Head and ARM use one loop implementation or specialized loops behind a shared executive protocol?
- What unique capability would justify each new native component?
- Can Hermes be maintained as a recognizable upstream base plus injection layer, or does v3 require a cleaner package boundary?
- Define at least three viable architecture options, including maintenance, performance, security, migration, and plugin implications. Recommend one only from evidence.

### Models, subscriptions, and routes

- Verify current official existence, availability, CLI/API access, context behavior, subscription entitlement, model naming, and cache telemetry for every model/route mentioned in the hypothesis. Treat names such as Gemini 3.8 Flash, Composer 2.5, Luna, and other future models as unverified until a primary source supports them.
- Determine whether Cursor can expose third-party models through its subscription pool and what is observable/configurable from its CLI. Do not equate UI availability, OAuth, or an alias with flat-subscription execution.
- Separate model, provider, engine, account, capacity pool, billing basis, and host in every conclusion.
- Identify cache controls available through official APIs versus opaque CLI/harness behavior.
- Specify confidence states for unknown flat-subscription capacity and cache data.

### Context and compaction

- Compare native compaction in Codex/OpenAI, Cursor, Claude Code, Gemini CLI, OpenCode, Hermes, Pi, and DeepSeek Harness.
- Verify triggers, retained state, hooks/events, session portability, cache consequences, and repeated-compaction failure modes.
- Challenge the proposed Context Capsule, non-droppable kernel, Owner Intent Ledger, Context Capability Descriptor, and one-compaction-owner rule.
- Design falsifiable recall, continuation, rehydration, and token/cache experiments.
- Never claim cross-provider server-cache portability. Evaluate provider-neutral semantic artifact reuse separately.

### State, plugins, nodes, and security

- Validate whether one SQLite WAL writer plus artifact storage fits the expected event volume and target hardware.
- Compare plugin lifecycle/composition designs and define the smallest non-pluggable integrity kernel.
- Define durable versus ephemeral event boundaries and backpressure/failure containment.
- Threat-model node enrollment, signed goal envelopes, replay/fencing, disconnect behavior, credential brokering, plugin updates, project config, and egress.
- Preserve owner sovereignty and configurable full access while proving remote trust boundaries and preventing credential/data leakage.
- Keep the lightweight enrollment preflight separate from official deep conformance.

### Scientific optimization

- Turn every major performance, quality, quota, cache, compaction, delegation, and routing claim into a measurable hypothesis.
- Define representative public/synthetic task corpora, controlled comparisons, metrics, sample/variance expectations, and decision rules.
- Measure quality, quota, real cost, machine load, latency, and human review separately.
- Establish v2 baselines before assigning v3 numeric budgets.

## Required documentation outcomes

Improve the existing `docs/v3/` suite rather than starting a second competing spec. Add documents only when a distinct long-lived concern cannot fit cleanly in the map.

At minimum, produce or refine:

- a verified current-architecture and gap map with file/symbol/test citations;
- a source-to-v3 traceability matrix: current component -> retained invariant -> v3 owner -> migration -> gate;
- an evidence-pinned reference matrix with revisions, licenses, and adoption decisions;
- three or more native-runtime architecture options and a recommendation;
- a constitutional reconciliation list;
- a normalized glossary and object/event model;
- quantitative benchmark plans and provisional performance-budget method;
- a construction runbook separated from the product specification;
- a prioritized open-question list suitable for the next Grill Me session;
- an updated decision register that never converts hypotheses into accepted owner decisions.

Every factual claim must be one of:

- linked to current source/test evidence;
- cited to a primary external source with revision/date;
- explicitly labeled inference;
- explicitly labeled hypothesis/open question.

Do not cite the transcript as proof of external behavior. Use it only as provenance for Lucas's preferences and corrections.

## Anti-bloat and quality rules

- Prefer one clear contract over overlapping abstractions.
- Reuse proven v2 invariants but do not preserve code merely because it exists.
- Every proposed component must pass the Feature Admission and Resource Discipline contracts.
- Disabled optional features must have near-zero runtime cost.
- Avoid inventing implementation detail before the owning contract and experiment are understood.
- Preserve rejected/superseded reasoning so it is not rediscovered.
- Do not optimize for document count or length. Remove duplication and link to one canonical definition.
- Never use hidden chain of thought as architecture state or evidence.

## Checkpoints

At each meaningful research milestone:

1. Reconcile findings against the hierarchy and decision register.
2. Update docs with evidence and confidence.
3. Run the documentation gates below.
4. Commit a coherent docs-only checkpoint locally if clean.
5. Continue with remaining independent lanes.

If a material ambiguity requires Lucas, record it explicitly as `open` with options, trade-offs, evidence, and a recommended next Grill Me question. Continue unrelated research; do not guess or implement through the ambiguity.

## Machine-checkable completion gate

Before declaring completion:

1. `git diff --check` passes.
2. `git status --short` shows changes only under `docs/v3/`.
3. Every relative Markdown link under `docs/v3/` resolves locally; every external citation is direct, primary, and was checked during this run.
4. A secret/privacy scan finds no credential material, raw private-project content, local auth paths, or private repository identifiers.
5. No document silently amends `CONTROL_PLANE.md` or treats a hypothesis as ratified.
6. The corrected Head -> ARM Executive -> delegated agent hierarchy is consistent everywhere; no AI ARM Manager reappears.
7. The v3 product spec, temporary construction runbook, and future research are visibly separate.
8. The current architecture map distinguishes deployed, operational, source-only, test-only, proposed, and unknown behavior.
9. The reference matrix records pinned evidence and licenses.
10. The next implementation session can derive bounded tasks and gates without reading the session transcript.

Commit the final documentation locally with a clear message. Do not push or open a PR.

## Final report

Return:

- local branch and commit IDs;
- files added/changed;
- strongest verified architectural conclusions;
- hypotheses rejected or materially revised;
- constitutional decisions Lucas must review;
- prioritized next Grill Me questions;
- recommended first implementation milestone and its gate;
- exact verification commands/results;
- explicit confirmation that nothing was pushed, deployed, unpaused, or changed outside `docs/v3/`.
