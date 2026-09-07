# Standalone agent platform: next research brief

2026-09-06. Audience: Owner, next Astra research integrator and independent reviewers.
Status: repository mapping and research preparation; integrations and trials remain unproven.

Recursion's first usable release is a configurable platform across models, harnesses,
subscriptions, tools, workflows and machines. The target is the new architecture under
`docs/v3`. Earlier brainstorming references to "v2" mean this release. The terminal
interface must expose its capabilities; a dedicated graphical application follows later.

## Current Owner input

The completed [Mark 2 handoff](../mark2/handoff.md) and [answer record](../mark2/directions.json)
extend this brief. OR-026 through OR-035 settle seven critical compatibility names, installation
direction, persistent assistants, controls/plugins, relative recovery budgets, six update modes
and quality goals. Mechanisms and resource defaults explicitly assigned to research are not
missing questionnaire answers. Preserve the six outputs and ordered comparisons below.

## Accepted requirements

Native execution, upstream execution and combined workflows are first-release requirements.
Either execution mode must be independently useful on an eligible configured route.
An upstream-only installation must account for planning, implementation, review,
summarization and recovery analysis through that upstream route. No hidden direct API
connection or continuously thinking supervisor is permitted as an implementation assumption.
Ordinary storage, scheduling, process supervision and accounting are deterministic.

The product must retain maximum useful common and engine-specific capabilities. Investigate
shared runtime, adapter, supported upstream extension, native loop and coordinated implementations
before declaring a limitation. A basic wrapper's limitation is a research starting point.
All ten controls are required: streaming, questions, approvals, queued messages, active
steering, interruption, resume, forks, compaction controls and custom commands/plugins.

Configuration and plugins are architectural capabilities. Separate engines, tools, context,
memory, routing, delegation, verification, scheduling, placement and resource policy where useful.
Presets and detailed settings must show effective values, provenance, supplying component,
conflicts, lifecycle and recovery. Explore one plugin configuration with different native and
upstream implementations, including loss reporting and conformance tests.

Initial platform acceptance targets Windows and Linux; macOS is an additional test opportunity,
not evidence of support. Remote control, placement, distributed workflow stages and recorded-work
recovery are required. Personal workstations, dedicated servers, GPU hosts and approved cloud
workers are distinct resource profiles. Distributed model inference is a separate later study.

Responsiveness, subscription efficiency and task completion are the Owner's default priorities,
subject to correctness, authorization, resource limits, privacy and recoverability. Report all
optimization dimensions and tradeoffs; do not invent scalar weights or numeric budgets.
Developers lead initial audience validation; novice setup and eventual organization needs inform
the shared architecture. Market demand and industry advancement remain hypotheses.

## Six deliverables and closure gates

| Deliverable | Starting artifact and required next-round result | Closure gate |
|---|---|---|
| 1. Product/capability map | [Repository map](repository-map.md): existing code, inert fixtures, specified contracts, revisions and unknowns; every feature traced through both modes and extensions | Every requirement has implementation ownership, config surface, next test and release milestone |
| 2. Execution/interaction contract | [Proposed contract](interaction-contract.md): state, roles, ten controls, composition, updates, evidence and remote transitions | Counterexample cases resolved; no undeclared reasoning path; model mapping preserves M1 identities and ambiguity |
| 3. Verified integration matrix | [Integration evidence](integration.json), extending the historical [matrix](../compatibility.json), with [source findings](report-source.md) | Pin tested build/interface/config/host; separate source-documented, observed, unsupported and unknown; technical support and usage/distribution eligibility have separate evidence |
| 4. Architecture comparisons | [Architecture roadmap](architecture-roadmap.md): reuse/adaptation/new implementation with removal criteria | Small interface probes inform formal-model freeze; formal model -> language comparison -> storage comparison remains ordered |
| 5. Preregistered trials | [Trial designs](trials.json): website, bug fix, interrupted refactor and upstream-only workflow | Frozen workloads/routes/evaluators, matched total budgets, failures included, uncertainty and stop/adoption rules recorded before execution |
| 6. Implementation/research roadmap | [Milestones and innovation queue](architecture-roadmap.md) | Every addition serves a capability, discriminating experiment or measured improvement; advanced features retain explicit milestones |

## Work sequence

1. Revalidate the clean worktree, Owner input and source versions. Read CONTROL_PLANE, applicable
   instructions, ANCHOR, this brief, the repository map and prior foundation/model evidence.
2. Complete narrow source gaps for Codex App Server, Claude binary plus supported extensions,
   Claude Agent SDK, Cursor ACP and OpenCode server/plugins. Maintain broader candidate coverage
   for Gemini, Hermes, DeepSeek Harness, Grok Build and Muse Code. The Owner has resolved the
   earlier "Meta" referent to Muse Code; technical and licensing facts still require verification.
3. Prepare minimal probe packets for the most consequential unknowns. Each specifies exact
   binaries/configuration, synthetic task, auth/billing path, data classification, allowed effects,
   capture method, cap, stop condition and cleanup. Probe output is disposable evidence; it does
   not select a production language or store. No live probe was executed in this preparation.
4. Incorporate observed counterexamples into the execution contract; then execute the already
   defined bounded formal model. Keep immutable M1 artifacts and OR-015's blocked broad writer
   migration intact. A contract conflict becomes an explicit repair proposal.
5. Freeze neutral vectors, compare CPython/Rust/Go, then JSONL/CAS against SQLite-WAL/CAS.
   Compare workflow libraries as optional implementations without outsourcing canonical ownership.
6. Run admitted platform trials and update claim/source records, limitations and release gates.
   Independent review checks the exact resulting candidate and all consequential evidence.

The original foundation campaign's prohibition on product implementation, provider probes,
node enrollment and new spend remains in force for this preparation. The next probe packets
must name any additional execution authorization they need; an experiment design is not a
record of a run. Public retrieval uses generic questions only. Do not send private repository
text, Owner messages, infrastructure identifiers or credentials to public services.

## What the Owner has settled and what remains open

The release name, native-loop requirement, equal importance of upstream execution, upstream-only
role accounting, ten controls, remote baseline and default ranking are settled. Do not ask them
again. The historical ten pending answers in the September 5 packet remain an immutable
snapshot; this clarification supersedes their resolved portions, not every proposed implementation.

Still open: model/broker proof boundary; exact certified engine set and version window; tradeoffs
when a required feature cannot be composed through any eligible mechanism; verifier independence
classes for a single-engine installation; update/rollback guarantees; and measured default
budgets. Researchers should first supply evidence and concrete options.

The first evidence question is: can one eligible upstream route carry every required reasoning
role and interaction without an undeclared connection, weakened guarantee or unacceptable
overhead? The first formal-model decision remains the aggregate/broker boundary; retain
abstract bounded flow whichever proof split is selected.

## Evidence limits and completion

This preparation maps and revises requirements, verifies selected primary interface mechanisms,
and leaves executable documentation checks. It does not provide integration certification,
benchmark results, a working native runtime, fault-tolerant remote execution or product-market
evidence. The next round is complete only when all six deliverable gates have evidence or a
precise unresolved gap, and its exact candidate passes the required checks/review.
