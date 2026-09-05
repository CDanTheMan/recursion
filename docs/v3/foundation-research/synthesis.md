# Standalone harness foundation synthesis

2026-09-05. **Verdict: ready with named evidence gaps for GRILLME.** Recursion has a coherent
foundation for a standalone product that can also govern upstream harnesses. It has not yet
proved an integrated runtime, comparative efficiency, complete effect control or market demand.
The six integration obligations below must be explicit before the formal-model freeze.
No Owner answer is supplied by this campaign.

The accepted small deterministic kernel and Recursion-owned canonical recovery remain the
right research baseline (OR-018, OR-019). The audit found no counterexample that requires
reordering **integration-contract audit → formal model → language comparison → storage
comparison → canonical-state construction**. A complete native agent loop is still an
experimental choice, not a consequence of “standalone.”

## One product, two execution modes

Standalone means Recursion can boot, inspect goals, replay evidence, reconcile or refuse
uncertain work, and recover without an upstream harness. Useful inference still needs an
eligible model route. With direct APIs, a native Recursion loop would own sampling, prompts,
tool dispatch, conversation and compaction. That gives more controllable interfaces and
more implementation responsibility; BYOK alone does not supply a working agent loop.

As a layer above a harness, Recursion owns the CLI, goals, authority, task admission, canonical
evidence and recovery. The upstream engine owns sampling and some native session/tool behavior.
A server/SDK can provide typed interaction; structured headless execution usually exposes less;
terminal passthrough exposes bytes and requires explicitly restricted scope.
See the ownership table and 238 capability cells in [compatibility.json](compatibility.json).
All are documentation, inference or required probes; none claims an observed integration.

The important product accommodation is one command bus with versioned capability extensions.
Core commands act on Recursion state. Imported engine commands need namespaces, argument
schemas, declared translation losses and mapped grants. A proposed namespaced compact command
may request native compaction, but cannot replace the canonical capsule silently. Queued input
and active-turn steering need different controls and turn/epoch correlation. An unavailable
capability must be visible before work admission. Do not silently fall back from governed work
to terminal passthrough. These are proposals under FND-004/FND-005, not implemented behavior.

Claude illustrates the difficulty particularly well. Current Anthropic guidance distinguishes
SDK/product authentication from running its unmodified binary. Third-party SDK products use
API/cloud credentials; the unmodified Claude Code route can let end users complete native
sign-in with their own eligible credentials, subject to its hosting/distribution conditions.
Recursion should not collect or intermediate those tokens or usage. Preserve the optimized CLI
through supported controls, without claiming native-feature parity. Codex supports ChatGPT and
API authentication, but technical login support is not a universal OAuth or subscription
portability promise. [Anthropic guidance](https://code.claude.com/docs/en/legal-and-compliance),
[Codex authentication](https://learn.chatgpt.com/docs/auth). FND-006.

Configuration is part of that contract: Claude Code's bare mode excludes subscription login,
while safe mode retains authentication but removes custom bridge extensions. Faster startup
alone cannot select a profile. Direct CLI, command, session and permission sources now ground
the binary matrix independently of SDK documentation. Exact mode, controls and overhead still
need the preregistered adapter trial. [CLI reference](https://code.claude.com/docs/en/cli-reference),
[headless operation](https://code.claude.com/docs/en/headless).

A visible tool event or approval callback does not prove control of shell descendants, an
engine's internal retries or independent network activity. The required fence must reach the
resource performing the effect. Otherwise narrow the task/resource scope or refuse the route.
Cancellation acknowledgment, process exit and stream loss leave external outcomes unresolved
without evidence. This restriction applies to native loops too; owning the dispatcher does not
automatically contain arbitrary subprocesses. FND-003/FND-005.

## What must precede formal-model freeze

The merged M1A/M1B/M1C candidates and receipts are ancestors of this campaign. Their pure/inert
implementation bytes and fixture digests match their reviewed boundaries; fresh baseline M1
and v2 regressions passed. This is substantial contract evidence, not a deployed v3 runtime.
M1C's fabric-only fixture does not resolve OR-015's missing common writer fence. FND-001.

The model integration contract must:

1. Project M1A abstract effects into M1C intent/trace identities without dropping goal, plan,
   packet, idempotency, attempt, admission, fence or ambiguity information.
2. Separate canonical writer fences, work leases, process/daemon epochs and PAUSE/admission
   epochs, and identify which resource consumes each.
3. Keep one canonical aggregate writer explicit; hash chains and equal projections do not
   prove writer authentication or exclusion.
4. Model current-immediate PAUSE as the operative policy. Representable future modes confer
   no permission. The Owner's scope ruling for this repository research does not alter runtime policy.
5. Preserve uncertainty under partition, missing receipts and partial process termination.
   Reconnect revalidates authority; no blind retry or disconnected publication.
6. Include bounded broker flow/replay state or declare a separate adapter proof obligation.
   A detected gap requires RESET; slow views cannot stall canonical append.

Retain E-FHAR2-101's finite bounds, guard-removal counterexamples and explicit fairness cases.
Do not assume that the Owner, provider or network eventually responds. The precise mapping
proposal and red designs are in [evidence.json](evidence.json), under
`analysis.foundation.model` and the model fixture entries. These are new model-level
obligations, not edits to immutable M1 schemas. FND-002.

## Consequential evidence corrections

The benchmark is the **Artificial Analysis Coding Agent Index**, v1.4. The retrieved
Opus 4.7 medium comparison reports OpenCode 51.28, Cursor CLI 46.66 and Claude Code 42.39.
Claude Code max reports 51.58 at about twice OpenCode's reported mean cost. Builds vary by
benchmark component; paired uncertainty and matched budgets were not recovered. This supports
a narrow medium-effort ranking, not universal leadership.
[Results](https://artificialanalysis.ai/agents/coding-agents),
[methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking). FND-018.

T3 is a web/desktop graphical product, not a TUI. OpenCode, DeepSeek Harness and T3 have
consequential upstream changes beyond the repository's earlier pins. Grok Build is now resolved
to an official Rust TUI/headless/ACP source release with Apache-2.0 first-party licensing;
Windows binary availability does not imply tested Windows source builds. Muse Code is a
plausible “Meta” referent, but the intended product remains unconfirmed. Exact source pins,
licenses, compare limits and revalidation triggers are in the canonical
[SOURCE-REGISTER](../SOURCE-REGISTER.md) and evidence records. FND-007.

Current Codex remote documentation includes Windows and Mac hosts. Cursor's desktop-start
requirement applies to Remote Control; Cloud Agents can start through other interfaces, and
My Machines is another execution-host route. Attach, steer, start, approve, resume and unattended
boot must be checked separately. Host availability and service rollout still matter.
[Codex Remote](https://learn.chatgpt.com/docs/remote),
[Cursor Remote Control](https://prod.cursor.com/docs/cloud-agent/mobile),
[Cloud Agents](https://cursor.com/docs/cloud-agent). FND-013.

Context capacity, native conversation, durable goals, retrieval memory and provider caches are
different resources. Neither a universal 90% discount nor a universal 30-minute semantic drain
is supported. Astra's current API long-input price boundary is more than 272K input tokens,
distinct from its 1,050,000-token capacity. OpenAI, Anthropic and Gemini retention/write/read
rules differ. No subscription quota savings can be inferred from API prices.
The detailed accounting partition and edge cases are in `analysis.foundation.economics`.
[Astra reference](https://developers.openai.com/api/docs/models/gpt-6-astra),
[OpenAI caching](https://developers.openai.com/api/docs/guides/prompt-caching),
[Anthropic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
[Gemini caching](https://ai.google.dev/gemini-api/docs/caching). FND-009–FND-011.

Layered compaction already fits the capsule/fidelity contract, but its benefit remains unproved.
Use one compaction governor per route epoch, preserve non-droppable control state, and reject
unfaithful summaries. Reasoning text, summaries, opaque state and token counters are separate
types; canonical recovery cannot depend on hidden reasoning. Persistent Head/ARM actors can
react to events and deterministic health checks without continuous model calls. FND-009/FND-014.

## Compatible accommodations and later work

Preserve Lucas-first validation and one product with optional profiles. Developers need
inspectable changes and recoverable interruptions; casual users need comprehensible setup,
cost and permission boundaries; organization operators additionally need identity, audit and
support controls. Hosted multi-tenancy introduces separate authority and isolation requirements.
None of this demonstrates demand, willingness to pay or compliance. FND-008.

Keep deterministic zero-model setup as the bootstrap and recovery path. An optional assistant
may explain presets and propose scoped configuration changes after authentication; it must
not see credentials or become necessary offline. Profile actual desktop lag across UI, engine,
indexers, language servers, tools and inference before choosing a remedy. Orchestration itself
need not require a GPU; optional local inference has separate hardware requirements. FND-012.

The eight [preregistered experiments](experiments.json) cover compaction fidelity, total cache
economics, fleet allocation, resource/UI cost, native-versus-upstream adapter control, node
faults, setup comprehension and upgrade certification. They include single-agent and simple
delegation baselines, failures and human review costs. Repeated attempts are not independent
tasks. Proposed Astra/Sol/Luna/Muse profiles are treatments, not permanent authority levels.
Historical scientific studies motivate these controls; they do not establish Recursion outcomes.
FND-015/FND-017.

Defer hosted tenancy, commercial tiers, graphical/media product expansion, automatic publication,
universal native command/plugin compatibility and periodic model keepalives. Reject automatic
stronger-model authority, hidden-reasoning displays, stale-result cache manipulation and
“process killed therefore effect rolled back.” Preserve current authority and publication rules.

## Next decision

Begin [GRILLME](grillme.md) with the model-boundary decision: keep the smallest canonical
aggregate and make broker flow a separate adapter obligation, or include bounded broker state
in the initial model. The recommendation is the former unless a concrete coupling counterexample
requires the latter. All ten answers remain pending in [decisions.json](decisions.json).

The remaining gaps are named, not disguised as success: exact Meta identity, several binary/SDK
versions, callback coverage and command fidelity, endpoint-specific counter normalization and debit observations,
performance/market evidence, model refinement and real resource fencing. Review uses the
authorized native fallback if external-family privacy/route eligibility cannot be verified.
This limits provider diversity; it does not change the experiment sequence or authorize runtime work.
