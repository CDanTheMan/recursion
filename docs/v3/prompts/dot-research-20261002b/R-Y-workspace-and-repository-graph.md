---
title: R-Y — Workspace and repository graph
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-Y — Workspace and repository graph

This is a workspace-and-source-graph handoff for accepted Owner decisions D-018, D-019, D-022,
D-024 and D-031, with the gap register in [GAPS.md](../../research-lane/GAPS.md). It builds
directly on [R-O](R-O-performance-and-configurability-engineering.md), the
backend-performance handoff, and on [R-K](R-K-terminal-multiplexer-and-tui.md), the terminal-
multiplexer handoff, and must extend rather than restate them: R-K places a workspace in views,
while R-Y designs the **workspace and repository model** those views project — how Recursion
identifies a workspace, binds a task to it, tracks changes and sources, and keeps that identity
stable across worktrees, monorepos, forks and snapshots.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on
2026-09-28 (state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the
executive control plane. Workers are bounded executors. An implementer's own PASS is never
acceptance; independent review is required, and missing verification is never a pass.
`CONTROL_PLANE.md` is the operative constitution; a research session may propose amendments
but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or
merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- The object of study is the **workspace and repository graph**: the stable identity of a
  workspace, the repositories and worktrees it contains, the change and source graph over them,
  per-repository profiles, Git integration, source snapshots and forks, ownership, and the rule
  by which a task binds to one workspace identity.
- D-018 makes Recursion a first-class native harness *and* a first-class unifying wrapper whose
  purpose is to remove lock-in and cut quota/usage burn. The workspace model must be
  provider-neutral and forge-neutral: it must not privilege one code host, one version-control
  product or one vendor's workspace abstraction, and it must be able to describe a workspace of
  local repositories as well as hosted ones.
- D-019 ships every capability as an **opt-in plugin or profile** with no default spend. Source
  indexing, graph construction, repository profiling and snapshot maintenance are opt-in; binding
  a task to a workspace must add no inference, no indexing and no activation by default, and a
  disabled indexer must be inert.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. Workspace operations must not be confused with Stop: detaching a
  workspace view, switching worktrees or closing a checkout is not a Stop, and a workspace
  operation must never be read as terminating the actor behind a task.
- D-024 makes **productive continuity** the headline measurable differentiator across harness
  change, compaction, a **source fork** and a lost machine. The workspace graph is what "source
  fork" continuity acts on: a task must survive a fork, a worktree move, a snapshot restore or a
  repository rename while preserving authority, evidence and honest accounting, and must identify
  exactly which source revision and change set it ran against.
- D-031 forbids a "vendors sabotage quota" claim: repository size, index cost and traversal
  figures are reported as measured facts and honest counters, never as vendor-intent narratives.
- Authority is not origin-based: a repository path, a worktree, a branch name, a remote, a
  signed commit or a previously used workspace **confers no authority**; a task receives only the
  attenuated grant its GoalSpec authorizes, and a workspace binding does not widen it.
- Already accepted direction this lane must respect: the canonical writer defines the
  authoritative event order; the non-droppable control kernel pins the exact repository/source/
  candidate identifiers; source snapshots and rehydration locators are content-addressed and
  privacy-scoped; cross-project deduplication is forbidden for private content even when bytes
  match; and every recommendation carries a competing option, a decisive falsifier and a
  non-proof.
- Recorded evidence this lane inherits: the repository-map invalidation accuracy by commit and
  configuration digest is a required-but-unrun experiment in `CONTEXT.md`; DS-12 records the
  context/compaction suite as unrun; DS-21 records that no store is selected, so snapshot and
  digest durability are unmeasured; and the worktrees and task-graph affordances already exist
  elsewhere (D-024 and the 2026-10-02 strategy), so novelty must not be claimed for them.
- Prior comparison coverage to extend, not reinvent: the worktree dispatch and closed-view-versus-
  deletion behavior in the Grok Build Agent Dashboard, the worktree and projected-history fork
  behavior in OpenCode and the Codex TUI, and the Git object model (commits, trees, blobs, refs,
  worktrees, sparse checkout, submodules). These are cited from public documentation, not adopted
  or endorsed.
- Evidence status: no workspace identity resolver, repository map, change graph, snapshot or fork
  binding has been implemented or measured by Recursion for this lane. Every invalidation,
  scale, cost and fidelity statement below is to be established from public source, the Git
  documentation and a synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **workspace and repository-graph design candidate** for Recursion. The
lane specifies workspace and repository identity; multi-repository and worktree modeling; monorepo
scale and traversal; the change and source graph over files, commits, branches and workspaces;
per-repository profiles and configuration resolution; Git integration boundaries; source snapshots
and forks with content-addressed, privacy-scoped locators; ownership and visibility; and the exact
rule by which a task binds to one workspace identity and records the source revision it ran
against. It compares competing identity and graph designs (path-based, remote/URL-based,
commit-and-tree-addressed, workspace-manifest-based) with a decisive falsifier for each and
selects none. It delivers a design candidate with provider-free fixtures. It does not select a
language, store, framework, version-control integration, filesystem watcher or vendor, does not
qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, version-control system, code host,
filesystem watcher, index engine or vendor.** Do not decide an Owner question recorded in D-018,
D-019, D-022, D-024 or D-031. No provider, model or account call is made; no repository is cloned,
fetched, indexed or modified; no credential or account is touched. Do not claim that a path,
worktree, branch, remote, signed commit or prior workspace confers authority; a workspace binding
does not widen a task grant. Do not assert measured invalidation accuracy, index cost, traversal
performance or snapshot fidelity; record each as `unknown` until measured. Do not request or
display private repository content, local paths or host identifiers.

## Inputs to read

None from this repository: the rescope, the capsule and source-identifier semantics, the
privacy-scoped locator rules and the continuity endpoints are summarized in `## Baked context`
above, and no repository, connector or private-source access is assumed. The session must,
however, retrieve the public documentation it cites — the Git documentation for the object model,
worktrees, sparse checkout, submodules, refs and packfiles; the public documentation of the
code hosts and workspace abstractions named in the comparison; the worktree and fork behavior of
the public upstream harnesses; the public guidance on repository maps, content-addressed storage
and filesystem change notification; and the public monorepo scale and build-graph literature —
and pin each claim to a URL and retrieval date.

## Research questions

### Workspace and repository identity

1. What is the stable identity of a **workspace** and of each **repository** in it — rooted in
   content-addressed revisions, a workspace manifest, or both — such that identity survives a
   path move, a rename, a clone, a worktree change and a machine change without accidentally
   merging two distinct workspaces or splitting one?
2. What is the identity of a **source snapshot** and a **fork**, and how is it distinguished from
   a mutable working tree, a branch pointer and a remote, so that a task can name the exact source
   revision it ran against and later prove the same bytes were reproduced?
3. How are identifiers scoped and randomized so that private content exposes neither raw content
   digests nor stable size/timing patterns that make equality or membership practical to test, and
   how is cross-project deduplication forbidden for private content even when bytes match?
4. How does a task **bind** to a workspace identity — what is the binding record, what pins it
   (revision, profile, configuration digest), when is it re-resolved, and how is a stale or
   ambiguous binding refused rather than guessed?

### Multi-repository, worktrees and monorepo scale

5. How is a multi-repository workspace modeled so that a task can span repositories with an
   explicit, recorded dependency or coupling, without assuming one repository or one code host?
6. How are **worktrees** modeled as first-class, disposable execution contexts bound to a
   workspace identity, so that parallel tasks each get an isolated checkout while sharing one
   repository identity, and how is a worktree move or deletion handled without losing task
   continuity?
7. What monorepo scale must be addressed — repository size, file count, history depth, sparse and
   partial checkout, submodules or vendored trees — and how is traversal or indexing made bounded
   and incremental rather than a full walk on every task (D-019: no default indexing)?
8. How are per-repository **profiles** resolved and scoped — build/test/lint/tool configuration,
   eligibility, ignore and secret-exclusion rules, and language/ecosystem hints — and what is the
   precedence when a workspace profile and a repository profile disagree?
9. How is the workspace kept consistent under concurrent tasks: read/write isolation between
   worktrees, change detection without a globally coherent index, and a rule for who may mutate a
   shared checkout?

### The change and source graph

10. What is the **change graph** — tasks, change sets, revisions, reviews, effects and their
    causal/inclusion edges — and how does it remain accurate under rebase, amend, squash, force
    push and branch deletion without pretending history is linear?
11. What is the **source graph** — repository -> worktree -> revision -> tree -> path -> blob, plus
    ownership, review and dependency edges — and which edges are authoritative versus inferred
    and re-derivable?
12. How is graph invalidation made accurate and cheap: what invalidates a cached map (commit,
    configuration digest, profile change, file move), what is the falsifier for an invalidation
    claim, and how is unknown coverage marked rather than silently treated as absent?
13. How are changes and sources labeled with provenance (generated, adopted, ported, forked) and
    ownership (author, reviewer, owner, license boundary) so that a result can be attributed
    without leaking private content?

### Git integration, snapshots and forks

14. What is the Git-integration boundary: which operations Recursion performs natively versus
    delegates to the user's Git, how it handles a detached worktree, a dirty tree, an in-progress
    merge/rebase, submodules, hooks and signing, and how it avoids becoming a second source of
    truth about history?
15. How are **source snapshots** taken and restored deterministically (working tree, index,
    untracked and ignored files, attributes, line-ending and filesystem-case differences across
    the accepted platform floors), and how is a snapshot tied to a content address and a
    rehydration locator?
16. How is a **fork** represented and resumed so D-024 source-fork continuity holds: a task
    continues in a forked workspace while authority, evidence and accounting carry over, and the
    original source is not mutated?
17. How does the design keep the workspace model forge-neutral and vendor-neutral, so no code
    host, version-control product or workspace abstraction is privileged, and what is the
    falsifier for a claim of neutrality?

### Task binding, ownership and provider-free fixtures

18. How does a task bind to a workspace identity across a harness change, compaction, a fork and a
    lost machine (D-024), and how is the exact source revision and change set reported in the
    task's evidence and handoff?
19. What ownership and visibility model applies — who owns a workspace, who may see it, how
    delegated upstream harnesses are constrained to the authorized workspace, and how a task
    prevents cross-workspace content from leaking into an unauthorized context?
20. What provider-free fixtures must accept or reject: a workspace-identity stability fixture
    across a path move and rename, a distinct-workspaces-don't-merge fixture, a worktree parallel
    isolation fixture, a stale-binding refusal, a graph-invalidation-on-commit fixture, a
    snapshot/restore round-trip, a fork-continuity fixture, a dirty-tree and in-progress-merge
    handling fixture, a vendor-neutrality probe, and a secret-exclusion fixture — and what is the
    exact pass/fail predicate for each?
21. How do the fixtures prove that binding a task adds no inference or indexing by default, that a
    disabled indexer is inert, that no workspace binding widens authority, and that no private
    content or local path leaves its authorized scope — using synthetic repositories only, with no
    provider call?
22. What does the workspace and repository graph explicitly **not** prove: no claim that a
    snapshot captures every host or environment input, no measured invalidation accuracy or index
    cost, no guarantee of cross-forge equivalence, and no semantic correctness of a change set?

## Deliverable

A workspace and repository-graph design candidate containing: a workspace and repository identity
section defining stable workspace/repository/snapshot/fork identity, privacy-scoped locators and
the task-binding record; a multi-repository, worktree and monorepo-scale section defining
multi-repo modeling, first-class worktrees, bounded incremental traversal and per-repository
profile precedence; a change-and-source-graph section defining authoritative versus re-derivable
edges and accurate, cheap invalidation with `unknown` coverage; a Git-integration, snapshot and
fork section defining the integration boundary, deterministic snapshot/restore across platform
floors, and fork-continuity; an ownership, visibility and vendor-neutrality section; and a
provider-free fixture suite for every predicate above. Each identity, graph, snapshot and binding
recommendation names a competing option, a decisive falsifier and what it does not prove. No
language, store, framework, version-control system, code host, index engine or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, version-control system,
  code host, filesystem watcher, index engine or vendor.
- No claim that a path, worktree, branch, remote, signed commit or prior workspace confers
  authority; a workspace binding does not widen a task grant.
- No belonging to one code host, version-control product or workspace abstraction; the model is
  forge-neutral and vendor-neutral, with a falsifier.
- No default source indexing, graph construction or repository profiling; all are opt-in, and a
  disabled indexer is inert with zero effect (D-019).
- No treatment of a workspace operation (detach, switch, worktree change, view close) as a Stop;
  stop semantics follow D-022 only.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No provider, model, credential or account call; no repository cloned, fetched, indexed or
  modified; every fixture is synthetic and provider-free.
- No claim of measured invalidation accuracy, index cost, traversal performance or snapshot
  fidelity; each is `unknown` until measured.
- No new executive tier and no standing autonomous executive.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no reopening of the accepted context
  and capsule semantics in `CONTEXT.md`.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The identity section defines stable workspace, repository, snapshot and fork identity that
  survives path move, rename, clone, worktree change and machine change; distinguishes a snapshot
  from a mutable working tree; gives privacy-scoped locators; and defines a task-binding record
  that pins revision, profile and configuration digest and refuses a stale or ambiguous binding.
- The multi-repository section defines multi-repo coupling, first-class disposable worktrees bound
  to one repository identity, bounded incremental traversal for monorepo scale with no default
  indexing, and per-repository profile precedence over a workspace profile.
- The graph section defines the authoritative change graph and source graph, their authoritative
  versus re-derivable edges, provenance and ownership labels, and an invalidation rule with an
  `unknown`-coverage marker and a falsifier.
- The Git-integration section defines the native-versus-delegated boundary, handling of detached
  worktrees, dirty trees, in-progress merge/rebase, submodules, hooks and signing, and avoids
  becoming a second source of truth about history.
- The snapshot and fork section defines deterministic snapshot/restore across the accepted platform
  floors, a content-addressed locator, and D-024 source-fork continuity where authority, evidence
  and accounting carry over without mutating the original source.
- The ownership and neutrality section defines workspace ownership and visibility, constrains
  delegated upstream harnesses to the authorized workspace, and states that the model privileges
  no code host, version-control product or workspace abstraction, with a falsifier.
- Tasks bind to a workspace identity and report the exact source revision and change set across
  harness change, compaction, fork and lost machine.
- The provider-free fixture suite specifies predicates for identity stability, distinct-workspace
  non-merge, worktree isolation, stale-binding refusal, invalidation-on-commit, snapshot/restore,
  fork continuity, dirty-tree/merge handling, vendor neutrality and secret exclusion, and no
  fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, version-control system, code host, index engine or vendor is
  selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured invalidation accuracy or
  index cost, no capture of every host/environment input, no cross-forge equivalence guarantee and
  no semantic correctness of a change set.
- Protected paths are untouched; privacy and secret scan are clean.
