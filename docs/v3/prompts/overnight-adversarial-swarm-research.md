---
title: Overnight Codex prompt — adversarial Recursion v3 architecture swarm
status: superseded-do-not-run
last-updated: 2026-09-02
target-duration: 7–8 productive hours, hard stop at 8 hours
superseded-by: ../FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md
---

# Overnight Codex prompt — adversarial Recursion v3 architecture swarm

> **Do not run this prompt.** It predates `OWN-FHAR-001`, the proposed Recursion Head identity,
> the planning-contract baseline, and the completed frontier-harness campaign. It remains only as
> provenance; use the active campaign artifacts and a newly authorized bounded prompt instead.

Copy everything below the divider into a new Codex task opened on the existing local
`codex/v3-design-foundation` worktree. This prompt assumes the branch descends from the
local documentation commit `6ce6fbb`; a newer docs-only descendant is acceptable and must
not be reset.

---

You are the lead architecture researcher and evidence integrator for an explicitly
authorized, documentation-only Recursion v3 control-plane authoring session.

Your job is to run a resource-aware, cross-family research swarm for approximately eight
productive hours and leave the existing `codex/v3-design-foundation` branch ready to drive
a separately authorized autonomous construction session tomorrow night. Eight hours is a
hard ceiling and an opportunity for deeper verification, not permission to idle, pad work,
or consume quota after the completion gate has passed.

## Parent goal and definition of success

Turn the current v3 hypotheses into an adversarially reviewed, source-grounded architecture
package. At completion, another agent must be able to understand the real v2 system, the
proposed v3 destination, the migration path, the unresolved owner decisions, the first
construction milestones, and their machine-checkable gates without relying on this chat or
hidden reasoning.

Success requires all of the following:

1. The current system is traced from live source, tests, schemas, Git history, and deployment
   evidence where read access is already available. Unknown deployment state stays unknown.
2. Major architectural claims are challenged by a different model family from the family
   that proposed them.
3. External claims use direct primary sources pinned by date, version, tag, or commit when
   possible. Repository claims cite files, symbols, tests, and the inspected commit.
4. Disagreement is resolved by evidence and explicit trade-offs, never by model majority.
5. The documents distinguish verified fact, inference, hypothesis, proposal, accepted owner
   direction, and unresolved decision.
6. No runtime code, control-plane authority, provider configuration, credentials, deployment,
   or remote system state is changed.

Quality, correctness, privacy, and low quota burn outrank speed. Prefer deterministic local
inspection and targeted primary-source retrieval before asking another model to synthesize.

## Exact branch and authority boundary

Work only in the existing local worktree for:

- branch: `codex/v3-design-foundation`
- expected starting commit: `6ce6fbb` or a newer docs-only descendant
- expected base: `origin/master` at or descended from
  `98113d6c6d3debe2a4d207c51bb1780f7356d714`

Do not reset or discard newer work merely to match those hashes. If Git shows a divergent
branch, non-document changes after `6ce6fbb`, unresolved conflicts, or user-owned changes that
overlap `docs/v3/**`, stop before writing and report the exact mismatch.

Read `AGENTS.md`, `CONTROL_PLANE.md`, and `ANCHOR.md` completely before planning. This is the
one control-plane authoring session Lucas has explicitly approved, but those files remain
authoritative and outside the write boundary.

Allowed writes:

- `docs/v3/**`

Everything else is read-only. In particular:

- do not modify source, tests, schemas, `state/**`, `scripts/**`, config, auth, environment,
  cron, model/provider profiles, PAUSE, permissions, or the VPS;
- do not merge, rebase, reset, prune branches, deploy, restart, unpause, publish, open a pull
  request, or push;
- do not provision credentials or inspect/print secret values;
- do not spend metered API funds or enable a paid fallback merely to satisfy the requested
  model mix;
- do not access private project repositories or send private repository content to a
  contributor/training-data route;
- do not begin product implementation.

Local documentation-only checkpoint commits are allowed. The final state must be committed
locally and remain unpublished.

## Authority model that every output must preserve

```text
Lucas — principal
  -> Main Assistant / Head Hermes — portfolio executive
       -> goal-scoped ARM executives — plan, delegate, replan, checkpoint
            -> bounded agents and native/external harness sessions
                 -> machine gates plus independent verification
       -> deterministic Recursion kernel — authority, state, budgets,
          routing, leases, PAUSE, evidence, publication
  -> Lucas reviews, merges, provisions credentials, and deploys
```

Head Hermes directly creates and monitors ARM executives. There is no separate AI ARM
Manager. The kernel is a privileged deterministic enforcement substrate, not another
reasoning actor. Model escalation, provider failover, delegated worker creation, executive
replacement, and authority escalation are separate events. V3 is the only proposed release;
do not invent a v4 bucket.

The current `CONTROL_PLANE.md` remains the constitution. When a provider-neutral design
conflicts with a current constitutional clause, write a proposed reconciliation for Lucas;
never edit around it or describe it as already ratified.

## Mandatory route preflight — no substitutions

Run a read-only capability and privacy preflight before dispatching research. Record only
provider/model identifiers, CLI versions, success/failure, relevant limits, and source links.
Never record credentials, tokens, account identifiers, or raw authentication output.

Requested worker routes:

| Route | Intended use | Required behavior |
|---|---|---|
| Codex native `gpt-5.6-luna` | repository archaeology, synthesis, formal contract analysis | `xhigh` reasoning; normal/default service tier; no `fast` tier |
| OpenCode Go `opencode-go/muse-spark-1.3-contributor` | public-reference research and independent criticism | use this exact installed model identifier; never send private/unpublished repository content, the archived transcript, VPS details, credentials, owner identity, or local paths |
| Codex CLI custom-provider `grok-4.5` | adversarial architecture and threat-model criticism | normal/default service tier; use only an already configured, authenticated, non-metered route; probe whether the requested `xhigh` control is genuinely accepted and meaningful |

`nonfast` means the normal/default service tier. Do not invent a `nonfast` configuration
value, and do not set Codex `service_tier` to `fast`.

The Grok route is conditional. Its model existence is not proof that this local Codex CLI
has a working xAI provider profile, that a subscription covers it, or that Codex's `xhigh`
effort maps to xAI. Perform one minimal, read-only, non-secret-bearing probe using the
installed CLI and existing user-level configuration. Then:

- if `grok-4.5` and the requested reasoning control work on an already authorized non-metered
  route, use them and record the exact verified semantics;
- if Grok works but `xhigh` is rejected, ignored, or unverifiable, do not label it xhigh and
  do not silently change controls. Record the capability gap and omit that route unless the
  existing configuration already defines an owner-approved native equivalent;
- if authentication, provider configuration, or billing status is absent or unclear, do not
  change configuration and do not spend money. Record a blocker for that route and continue
  with Luna and Muse;
- never substitute Grok 4.6, another Grok alias, or a different model merely to preserve the
  number of workers.

The installed OpenCode model catalog is evidence for local route naming, not evidence of
privacy, billing, entitlement, or stable future availability. Because the Muse route is a
`Contributor` route, give it only public source material and purpose-written sanitized
briefs. It may research the public Recursion `origin/master` tree and public reference
repositories, but it must not read the local unpublished v3 transcript or receive raw local
v3 documents. A Luna worker or the lead must convert any local question into a minimal public
or synthetic brief first.

If a requested route is unavailable, continue at reduced diversity. Never hide the failure,
silently substitute a model, weaken privacy, change auth/config, or activate a paid route.

Use these primary capability references as starting evidence and re-check their current
content during the run:

- Codex subagents and model/reasoning configuration:
  <https://learn.chatgpt.com/docs/agent-configuration/subagents>
- Codex configuration, custom providers, and service tiers:
  <https://learn.chatgpt.com/docs/config-file/config-reference>
- OpenAI Luna model capabilities:
  <https://developers.openai.com/api/docs/models/gpt-5.6-luna>
- OpenCode Go provider behavior:
  <https://dev.opencode.ai/docs/go/>
- xAI Grok 4.5 model documentation:
  <https://docs.x.ai/developers/models/grok-4.5>
- xAI Grok 4.5 announcement and availability claims:
  <https://x.ai/news/grok-4-5>

## Swarm topology and resource discipline

You are the sole integrator and the only writer. Use no more simultaneous workers than the
machine, provider limits, and installed Codex concurrency permit. Begin conservatively with
at most three research workers in addition to the lead only if resources allow. Reduce
concurrency immediately on sustained CPU, memory, disk, thermal, network, provider-throttle,
or interactive-performance pressure. Concurrency is a ceiling, not a target.

Use bounded waves. Do not launch recursive unbounded swarms. Reuse an existing worker for a
follow-up when that preserves useful context more cheaply than starting another. Give every
worker one question, source boundary, evidence format, timebox, and explicit non-goals.

Only the lead edits `docs/v3/**`. Native subagents return evidence packets. External CLI
workers run in read-only/sandboxed contexts and return text evidence packets; they do not edit
the shared worktree, commit, or launch their own agents. If the installed tooling cannot
guarantee that boundary, give it source excerpts or URLs outside the worktree instead of
repository access.

### Wave 0 — orientation and preflight, about 30 minutes

1. Verify branch, merge base, worktree cleanliness, remotes, and allowed paths.
2. Read the authority files and all current `docs/v3/**` documents.
3. Inspect installed CLI help/model catalogs and test only the minimal route preflights above.
4. Create a research queue and claim ledger skeleton. Assign claim IDs before broad research.
5. Establish the actual resource/concurrency ceiling for this machine without changing config.

### Wave 1 — independent discovery, about 80 minutes

Run up to three independent lanes:

1. **Luna xhigh — current-system archaeologist.** Trace the actual v2 control flow, actor
   hierarchy, planning, dispatch, adapters, state, reconciliation, gates, publication, CLI,
   and tests. Identify duplicate sources of truth and distinguish operational, source-only,
   test-only, documented-only, deployed, and unknown behavior. Cite commit, file, symbol, and
   test evidence.
2. **Muse Contributor — public harness researcher.** Using public primary sources only,
   compare T3 Code, DeepSeek Harness, Hermes Agent, Pi, Claude Code public material, OpenCode,
   and relevant public Codex/Gemini/Cursor material. Pin revisions/licenses and report concrete
   mechanisms worth adopting, adapting, or rejecting. Do not receive local v3 drafts.
3. **Grok 4.5 conditional — hostile architecture critic.** From a sanitized architecture
   brief, try to falsify the proposed Head -> ARM -> worker hierarchy, provider-neutral
   execution fabric, plugin split, node security, SQLite-first state, and context design.
   Look for hidden coupling, unsafe trust expansion, performance cliffs, and migration traps.

The lead performs independent local inspection while workers run. Do not merely wait.

### Wave 2 — cross-family adversarial review, about 75 minutes

Give each available family a compact evidence packet produced by another family, with private
or unpublished material removed before it reaches Muse. Require the reviewer to return:

- the strongest supported claim;
- the weakest or overstated claim;
- a source-quality audit;
- at least one plausible counterexample or failure mode;
- contradictory evidence searched for and found/not found;
- a corrected claim with calibrated confidence;
- the fastest decisive experiment or repository check.

No worker may approve its own claim. Preferred rotation is Luna reviews Muse, Muse reviews a
public/synthetic projection of Grok or Luna claims, and Grok reviews Luna. If one route is
unavailable, use a second independent Luna context plus deterministic source verification,
and disclose the reduced family diversity.

### Wave 3 — focused falsification and experiments-on-paper, about 75 minutes

Create short, non-overlapping lanes for the highest-risk questions discovered so far:

- v2-to-v3 authority and state migration;
- main-assistant/ARM executive contracts and escalation semantics;
- provider/account/model/engine/capacity-pool separation;
- compaction ownership, context capsules, intent retention, and cache observability;
- SQLite WAL writer, artifacts, event log, backpressure, and small-VPS resource budgets;
- plugin integrity kernel, dependency conflicts, editions, and disabled-feature cost;
- remote-node enrollment, signed goal envelopes, replay/fencing, credentials, egress, and
  owner-authorized full-access modes;
- autonomous-session checkpoints, quota exhaustion, bounded paid authority, failed gates,
  refusal/fallback events, and resume behavior.

Every lane must propose falsifiable tests and decision rules. Do not report imagined
benchmarks as measurements. Explicitly separate expected benefit from verified improvement.

### Wave 4 — architecture options and reconciliation, about 60 minutes

Synthesize at least three genuinely distinct v3 runtime options, including:

1. incremental extraction from the current Hermes-derived runtime;
2. a native Recursion kernel with compatibility adapters around existing loops;
3. a more complete native harness with external CLIs treated as provider-tuned plugins.

For each, compare product fit, user experience, code ownership, upstream-sync cost, failure
isolation, security, plugin surface, context behavior, migration risk, expected performance,
small-VPS viability, testability, and rollback. Recommend one architecture only after the
adversarial evidence pass. State what would falsify the recommendation.

Reconcile the recommendation with `CONTROL_PLANE.md`. List exact constitutional amendments
or ratifications Lucas would need to approve; do not edit the constitution.

### Wave 5 — documentation integration, about 90 minutes

Update the existing `docs/v3/` suite instead of creating a competing specification. Remove
duplication, strengthen canonical ownership, link related documents, and preserve provenance.

Add a document only if it has a distinct durable purpose. The final suite must contain,
either as new focused files or clearly identified sections in existing canonical files:

- a verified current-architecture/gap map;
- a v2 -> v3 traceability and migration matrix;
- an evidence-pinned reference and license matrix;
- the compared architecture options and recommendation;
- a constitutional reconciliation list;
- one normalized glossary and object/event ownership model;
- a provider-route capability matrix with uncertainty and expiry rules;
- a performance/resource hypothesis plan for workstation and Hetzner-class deployment;
- a construction runbook separated from product specification;
- a prioritized next Grill Me queue and owner decision list;
- a proposed first autonomous construction milestone with bounded tasks and gates.

Update `DECISION-REGISTER.md` without turning evidence, model consensus, or transcript content
into a decision Lucas did not make.

### Wave 6 — final hostile audit and closure, about 70 minutes

Dispatch the smallest available cross-family review set over the integrated architecture.
Reviewers must look specifically for:

- hallucinated features, models, entitlements, cache controls, measurements, and deployment
  state;
- contradictions with current source, tests, constitution, or accepted owner direction;
- privacy leakage or contributor-route contamination;
- accidental creation of an AI ARM Manager;
- hidden mandatory bloat, idle resource costs, or defaults that can drain subscription quota;
- unsafe remote-node authority or ambiguous credential ownership;
- non-falsifiable performance claims and missing rollback gates;
- implementation tasks too broad for autonomous delegation.

The lead adjudicates every objection using sources. Preserve material dissent in the claim
ledger when evidence does not resolve it. Run the completion gate, make one final local docs
commit, and stop. Do not use leftover time to invent more features.

## Evidence packet contract

Every worker response must be concise and use this schema:

```text
lane:
model/provider/engine route actually used:
scope and non-goals:
source boundary and inspected revisions/dates:
claims:
  - claim_id:
    precise claim:
    evidence: direct URL or repo commit/file/symbol/test
    evidence type: primary | source | test | measurement | inference
    supporting excerpt or observation: short paraphrase, not hidden reasoning
    contradicting evidence searched/found:
    confidence: high | medium | low
    expiry/revalidation trigger:
risks and counterexamples:
open questions:
recommended decisive checks:
privacy confirmation:
```

Do not ask for or preserve hidden chain of thought. Grounded findings require inspectable
evidence and a concise rationale, not private reasoning traces.

## Claim ledger and adversarial acceptance rules

Maintain one canonical claim ledger under `docs/v3/`. Each material claim needs:

- stable claim ID;
- exact claim and scope;
- classification: verified fact, inference, hypothesis, proposal, accepted direction, open;
- inspected source and revision/date;
- source quality and freshness;
- proposer route and independent reviewer route;
- strongest supporting and contradicting evidence;
- adjudication and confidence;
- affected architecture decisions/documents;
- revalidation trigger or expiry when time-sensitive.

A claim is `verified` only when:

1. the evidence directly supports the exact wording;
2. a different model family challenges it, when multiple families are available;
3. the lead independently opens the source or repository evidence;
4. contradictions are resolved or disclosed;
5. temporal/provider claims state the verification date and revalidation trigger.

Use at least one primary source for every external technical claim. Prefer two independent
sources for volatile provider, entitlement, pricing, or model-availability claims, but never
manufacture independence by citing pages that repeat the same announcement. Source code and
tests are primary evidence for repository behavior. Marketing copy is evidence of a vendor
claim, not independent proof of behavior.

## Architecture research requirements

Read the full v3 suite and the accepted v2 baseline, especially:

- `docs/recursion-v2-mvp-harness.md`
- `docs/architecture.md`
- `docs/delegation-design.md`
- `docs/plans/hermes-project-pilot-production-plan.md`
- `docs/plans/recursion-v2-execution-fabric.md`
- `docs/plans/engine-plugin-architecture.md`
- `docs/plans/remote-execution-adapters.md`
- relevant schemas, supervisor, pilots, reconciler, adapters, CLI, state, evidence,
  publication, and their tests.

Research public reference repositories from their upstream primary sources at pinned
commits/tags and record licenses:

- <https://github.com/pingdotgg/t3code>
- <https://github.com/deepseek-ai/deepseek-harness>
- <https://github.com/NousResearch/hermes-agent>
- <https://github.com/earendil-works/pi>
- <https://github.com/anthropics/claude-code>
- <https://github.com/anomalyco/opencode>

Also examine official public documentation/source for Codex, Cursor, Gemini CLI, and
`ccusage` only where a specific v3 question justifies it. Separate observed implementation,
documented interface, vendor claim, and inference.

At minimum answer:

1. What does Recursion v2 actually pursue and ship today, end to end?
2. Where are Head Hermes, Project Pilots/ARMs, workers, gates, state, escalation, publication,
   and human authority represented in source versus prose?
3. Which invariant contracts should survive v3 unchanged?
4. What is the smallest canonical v3 kernel, and what stays in plugins/adapters/external
   harnesses?
5. How should main assistant and ARM executives share an executive protocol without erasing
   their different authority and responsibilities?
6. How should configurable model depth, performance/price heuristics, subscriptions, API
   budgets, context, compaction, refusal fallback, and quota exhaustion interact?
7. Which context artifacts are provider-neutral, and which server-side caches are necessarily
   model/provider/account specific?
8. What can run efficiently on the intended Hetzner-class VPS, what belongs on a workstation,
   and what must be measured before numeric limits are chosen?
9. How can plugins and editions provide broad customization with near-zero cost when disabled?
10. What remote-node controls protect owner privacy, credentials, authority, and replay safety
    without locking owners out of open-source software?
11. Which portions remain inherited from Hermes Agent, which become maintained injections,
    and which require native Recursion ownership?
12. What bounded first implementation milestone most reduces architectural uncertainty?

## Anti-bloat and scientific discipline

- Prefer one canonical contract over parallel abstractions and duplicate state.
- Reuse proven v2 invariants, but do not preserve accidental complexity merely because it exists.
- Every proposed component must justify quality, performance, compatibility, security, or
  operator experience and state its disabled-path cost.
- Configuration does not excuse unsafe defaults or ambiguous authority.
- Make performance and quota claims as hypotheses until measured against a v2 baseline.
- Measure code quality, acceptance-gate pass rate, operator corrections, quota usage, metered
  cost, latency, cache observability, compaction recall, CPU, memory, disk, and I/O separately.
- Do not claim cross-provider server-cache portability. Evaluate stable-prefix construction
  and provider-neutral semantic artifacts as separate mechanisms.
- Do not copy another harness's design without license review, local fit analysis, and an
  explicit adopt/adapt/reject decision.
- Do not optimize for document count or word count. Anything the next implementation session
  cannot use should be removed or condensed.

## Machine-checkable completion gate

Before declaring completion, prove:

1. `git diff --check` passes.
2. All changes since the starting commit are under `docs/v3/**`.
3. Every relative Markdown link in `docs/v3/**` resolves locally.
4. Every material verified claim has a claim-ledger entry, direct evidence, independent
   challenge when possible, and lead adjudication.
5. Every external technical citation is direct and primary; its page/revision was opened in
   this run.
6. A privacy/secret scan finds no credentials, auth output, owner identifiers, private project
   content, raw local paths, or internal VPS secrets.
7. No contributor-route packet contains unpublished v3 documents, transcript content, private
   repository material, or sensitive infrastructure details.
8. The docs never imply that a route preflight proves subscription entitlement, future model
   availability, cache portability, or free metered usage.
9. `CONTROL_PLANE.md` was not changed or silently superseded.
10. The hierarchy is consistently Head Hermes -> ARM executives -> delegated workers, with no
    AI ARM Manager.
11. Product specification, temporary construction procedure, experiments, and unresolved
    decisions are visibly separate.
12. The recommended architecture names alternatives, evidence, dissent, falsifiers, migration
    steps, rollback boundaries, and expected disabled-path costs.
13. The first construction milestone is decomposed into bounded work with parent goal, allowed
    paths, explicit non-goals, acceptance gate, independent verifier, and stop conditions.
14. The final Git status is clean after one documentation-only local commit.
15. Nothing was pushed, merged, published, deployed, unpaused, or changed outside `docs/v3/**`.

## Stop and escalation conditions

Stop only the affected lane, preserve evidence, and continue independent work when a provider
or model is unavailable. Stop the whole session before writing or committing if:

- the branch/authority/write boundary is wrong;
- secrets or private-project data appear committed;
- safe source access would require changing auth/config or spending funds;
- current authority sources conflict in a way that makes documentation itself unsafe;
- overlapping user changes cannot be preserved.

Never work past the eight-hour ceiling. At 7 hours 30 minutes, stop launching research and
reserve the remaining time for source audits, privacy checks, link checks, reconciliation,
and a clean local commit.

## Final report

Return a concise handoff containing:

- elapsed productive time, branch, starting commit, and final local commit;
- routes requested, routes actually used, preflight outcomes, and any reduced-diversity caveat;
- files added/changed;
- strongest verified architectural conclusions and their claim IDs;
- claims rejected, weakened, or still disputed;
- architecture recommendation, falsifiers, and Hetzner/workstation fit conclusion;
- constitutional items and owner decisions requiring Lucas;
- next prioritized Grill Me questions;
- proposed first autonomous construction milestone and exact acceptance gate;
- verification commands and results;
- explicit confirmation that no secrets were exposed, no metered fallback was enabled, and
  nothing was pushed, merged, deployed, unpaused, or modified outside `docs/v3/**`.
