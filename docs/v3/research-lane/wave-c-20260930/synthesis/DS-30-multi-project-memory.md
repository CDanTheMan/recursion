# DS-30 — Multi-project supervision state and memory (synthesis)

## Provenance

- Raw report: `raw/ds-DS-30-multi-project-memory.md`.
- Source prompt: DS-30 — multi-project supervision state and memory.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented, inferred, proposal, and unverified/unknown.
- The report's confidence values describe research support, not probability. `unknown` is deliberate and is not zero.
- The report states it performed no implementation, repository change, provider/model call, scheduling action, or private-repository inspection.

## The question

How should Recursion v3 persist durable multi-project supervision state and memory, given that it already uses Git as transport and a durable `state/` tree under D-017, must preserve the D-entry decision log and morning-brief discipline, must support one operator supervising at least four concurrent projects, and must make `blocked`, `stale`, and `waiting-for-decision` explicit rather than inferred?

The report treats its task boundary as fixed: it may not select a language, database, framework, scheduler, numeric threshold, or budget, and may not make implementation or repository changes. It must also stay provider-neutral.

## Key findings

**(a) The strongest reconciliation is a canonical per-project semantic snapshot inside the existing `state/` tree**, paired with machine-generated observations, stable Owner-question records, and evidence receipts. Git history remains the transition history; the report explicitly proposes **no second append-only status log**. The D-entry log stays authoritative for accepted decisions, the morning brief stays the supervisory overview, and Git stays authoritative for HEAD, branch, working-tree, and fetch observations (all source-documented for the cited Git interfaces).

**(b) File survival is provider-specific.** The report distinguishes persistence on disk from survival in model context. Anthropic documents that its designated memory files are loaded at Claude Code startup and advises regular review; OpenAI documents that Codex aggregates `AGENTS.md`-family instructions into initial input (default aggregate limit 32 KiB) and compacts growing conversations by replacing prior input with a smaller representation. Neither establishes field-by-field survival of arbitrary status content through compaction — that is marked **unknown**.

**(c) Structured state does not yet have evidence of fewer resume errors than prose.** JSON Schema and YAML establish structural validation and a data representation, but the report located **no controlled primary study** comparing structured repository supervision state against freeform status prose on restart accuracy. The causal claim is therefore **unknown, not assumed**. The report's argument for structure is failure containment and mechanically diffable state, not a measured accuracy win.

**(d) Current state must be small, explicit, and authoritative.** A fresh supervisor should reconstruct the current WorkPacket, gate, authority, next action, unresolved evidence, exact pending Owner question, and freshness confidence without replaying a transcript or reading every historical file. Git-derived facts (branch, HEAD OID, dirty status, fetched refs, fetch success) must be **observed mechanically, never hand-copied** into semantic state.

**(e) `blocked`, `waiting_for_decision`, and `stale` are distinct.** `blocked` and `waiting_for_decision` are separate work-state kinds (the latter requires specifically an Owner-authority decision). `stale` is an orthogonal freshness classification with its own policy reference and signal references, so a project can be `blocked + fresh`, `waiting_for_decision + fresh`, or `active + stale`.

**(f) Long-horizon memory research argues against treating retrieval as truth.** LongMemEval reports roughly a 30% accuracy drop across sustained interactions and explicitly tests temporal reasoning, knowledge updates, and abstention; LoCoMo found long-range temporal/causal failures. Memora reports frequent reuse of invalidated memories and failures to reconcile evolving information. HiGMem, STITCH, and APEX-MEM are cited as architectural results, not grounds for selecting a store.

**(g) The conservative retrieval ordering is: namespace before similarity; current authority before history; summaries/indexes as candidate locators only; validity checks on every retrieved historical claim.** A candidate failing project namespace, resolvable source, non-supersession, or contradiction checks should yield `unknown` or escalation rather than an inferred answer. Any vector/graph/summary index must be a disposable derived cache, not truth.

**(h) Silent degradation is the key unattended-loop failure.** A running loop with a healthy heartbeat can still make no verified progress. The proposed rule: a cycle earns verified progress only when it produces evidence for an intended postcondition, advances an accepted gate/state transition, or resolves an explicit unknown/blocker. Its stated principal false-negative is an agent producing changing-but-wrong artifacts; it cannot replace Recursion's independent gate/review rule.

**(i) Scheduling is deliberately left open.** Classic cron persists schedule configuration but treats launches as fire-and-forget and does not track them; the distributed cron design adds durable launch tracking and idempotency. CloudEvents is scoped to event-format interoperability and does not define producer/consumer processing, delivery, replay, or crash semantics. Daemon crash-recovery is likewise **unknown** without a chosen runtime. The report's conclusion is scheduler independence, not a scheduler choice.

**(j) Guardrails are proposed with competitors and decisive falsifiers** for runaway loops, retry storms, context bloat, duplicate side effects, supervisor degradation, and wrong-memory retrieval. The supervisor-degradation case uses only deterministic outer observables (heartbeat, verified-progress receipt, open decisions, deadline/quota, worker completion) so recognition does not depend on the supervisor's own model memory.

## Recommendation and falsifier

The report recommends adopting, as an **additive convention under the already-authoritative `state/` tree**, four roles: `current.<structured>` (canonical semantic snapshot), `observed.<generated-structured>` (disposable machine observation), `questions/<id>` (durable Owner-question correlation), and `evidence/<id>` (verification receipt or provenance pointer). Directory names are illustrative; existing acceptable locations should be reused, and no serialization is selected.

The named competing option is a **freeform per-project status document as the primary operating record**, with blockers, decisions, progress, and repository observations maintained in prose.

The structured convention is **decisively falsified** if, under normal use across the intended multi-project workload, any of these occurs: a stale blocker is shown as current though durable evidence makes the contradiction detectable; an answered Owner decision is re-asked because the request could not be correlated to its resolution; two committed state revisions cannot be mechanically distinguished; a fresh agent cannot reconstruct current task, gate, authority, next action, and unresolved evidence without a transcript; a hand-maintained field disagrees with a Git-derived field; or derived retrieval silently imports another project's evidence or a superseded fact as current authority.

Merely avoiding those failures would not prove the syntax is optimal, that structured files intrinsically beat prose, that a particular database/index is warranted, or that any scheduler is superior.

## What this does not prove

- It does not prove schema-checked state reduces resume errors; that comparison is **unknown**.
- It does not prove structured files outperform prose, nor select JSON, YAML, or any other serialization.
- It does not select a scheduler, database, index, or framework; scheduler cost and event/daemon recovery semantics remain **unknown**.
- It reports no Recursion benchmark, runtime experiment, provider/model call, or private-repository inspection.
- Cross-project leakage rate is unmeasured; the transfer from conversational-memory benchmarks is an inference.
- Freshness thresholds are intentionally not invented; preference is explicitly left to operating policy.
- Real-world instruction-file staleness prevalence is unknown; the operator postmortem cited is anecdotal/unverified.

## Open Owner decisions

- Which concrete serialization represents `current`, `observed`, questions, and receipts.
- Which staleness signals are mandatory versus per-WorkPacket optional.
- What policy windows/thresholds classify a freshness signal as stale.
- Whether generated `observed` files are committed or regenerated on demand with selected receipts.
- The exact project-identity and archival lifecycle convention.
- Which questions require Owner authority versus ordinary resolution.
- Whether the morning brief is rebuilt entirely from `current + observed` or keeps human annotations.
- The evidence-retention/compaction policy for old receipts.
- Which unattended execution architecture is ultimately chosen.
- What constitutes an independently sufficient "verified progress" receipt per WorkPacket type.

## Relevance to later waves

- The semantic/derived separation (`current` vs `observed`), evidence receipts, and question correlation are reusable state-contract primitives for later waves.
- The "persist intent once, derive machine facts, reference decisions, keep views reconstructible" principle is a candidate cross-cutting invariant.
- The guardrail competitors/falsifiers and the crash/uncertainty vocabulary are natural model-checking and adapter-conformance targets.
- The open serialization, threshold, retention, and scheduler questions are candidates for explicit Owner decision records rather than further research.
