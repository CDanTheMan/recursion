---
title: Recursion v3 architecture-proof research agenda
status: ready-for-deep-research
last-updated: 2026-09-03
---

# Recursion v3 architecture-proof research agenda

## Purpose

The first architecture campaign grounded the v2 baseline and selected a provisional native
kernel plus adapter direction. The next campaign should prove or falsify the highest-risk
parts of that direction after the owner's 2026-09-03 rulings. It is research, not runtime
construction or constitutional amendment.

The audience is Lucas and the agent responsible for turning evidence into the v3 contract
milestone. The decision is whether the proposed actor, interaction, pause, permission,
verification, plugin, persistence and migration contracts are specific and defensible enough
to freeze schemas.

## Fixed owner direction for the campaign

Do not reopen these as model-opinion questions:

- Head and ARM planning may use any route inside an explicit owner-approved
  model/provider/account/capacity-pool envelope.
- Recursion v3 is its own headless harness; CLI is the canonical local surface, Telegram is an
  optional interactive surface, and no graphical frontend is required for v3.
- The CLI is interactive and supports several detachable terminal windows or panes. Terminal
  close detaches; it does not end the actor or process.
- An ARM is a goal-scoped executive that delegates a configurable fleet. One ARM per
  repository is a common default, not a protocol invariant.
- Direct owner-to-ARM conversation is a product requirement.
- PAUSE behavior and Full Access aggressiveness are configurable by explicit owner policy.
- Verifier independence is risk scaled.
- First-party/maintainer-approved plugins are signed by the installation trust root.
- Branch/worktree backlog limits are measured and configurable, not a universal constant.
- Recursion includes a research ARM capability that can discover papers, reconcile claims and
  design reproducible experiments under the same privacy/evidence contracts.
- The first private canary is `CANARY-01`, an owner-selected construction-domain project. Its
  real name, repository, source, prompts, branches and telemetry stay outside tracked/public
  research artifacts.

Current `CONTROL_PLANE.md` remains operative until separately amended. Research must state
where the desired v3 product policy differs from current private deployment authority.

## Optimization envelope

The campaign evaluates the whole product rather than optimizing a single benchmark. Every
dimension needs a v2/reference baseline, observable metric, quality or safety floor, competing
design, falsifier and revalidation trigger.

| Dimension | Research target |
|---|---|
| Verified work quality | First-review acceptance, escaped defects, repair cycles, gate strength, verifier disagreement and human acceptance |
| Model performance | Task-specific route suites, planning/implementation/review fit, tool success, long-horizon continuity, refusal and recovery |
| Context and cache | Repeated input, route-local cache evidence, session affinity, capsule fidelity, compaction loss, repository evidence reuse and hydration |
| Quota and cost | Subscription scarcity, metered authority, reservation value, retries, fallback, research cost and accepted-result efficiency |
| Runtime performance | Latency, throughput, CPU, RAM, GPU, disk/I/O, network, wakeups, process cleanup, WAL/replay and coordinator responsiveness |
| Lean codebase | Privileged/core lines and dependencies, binary/install size, startup imports, disabled-path work, duplicate mechanisms and maintenance surface |
| Configurability | Schema coverage, inheritance, provenance, live/checkpoint/restart application, safe presets, discoverability, migration and rollback |
| Reliability | Crash consistency, cancellation, attach/detach, provider/node loss, ambiguous effects, backup/restore, replay and fault containment |
| Security and privacy | Least/maximum authority, credentials, plugin supply chain, egress, project isolation, retention/deletion and auditability |
| Operator experience | Interactive latency, non-flicker display, causal communication visibility, explanation quality, accessibility and review attention |
| Portability | Windows/Linux behavior, terminal/CLI differences, provider/harness replacement, remote nodes and offline degradation |
| Scientific rigor | Primary sources, papers/standards, contradictory evidence, preregistration, reproducibility, uncertainty and negative results |

No weighted score may hide a failed quality, authority, privacy or recovery floor. Report the
dimensions separately before selecting a profile-specific trade-off.

## Research lanes

### R1 — headless native harness boundary

**Question:** Which semantics must Recursion implement natively, and which inner-loop features
should remain behind Codex, Claude Code, Cursor, Gemini, OpenCode, Hermes or other engines?

Compare turn lifecycle, tools, approvals, streaming, interruption, resume, subagents, context,
compaction, provider affinity, evidence extraction, offline testability, extension seams,
licenses and maintenance burden at pinned versions. Produce a responsibility matrix and one
minimal native-loop spike specification. Falsify the current Option 2 recommendation if a
required invariant cannot be enforced around an external engine or a native loop shows a
decisive measured advantage.

### R2 — direct and collaborative ARM conversations

**Question:** How should `#general`, dedicated ARM topics and multi-ARM rooms map onto durable
actors without introducing an AI ARM Manager?

Identify the exact GrokBot reference before using it. Research Telegram's primary API and
operational constraints, plus public multi-agent orchestration systems with explicit actor,
message, lease and authority models. Compare one-bot routing, one-bot-per-ARM and hybrid
topologies. Specify command addressing, shared-room coordination, disagreement, cycle
prevention, digesting, rate limiting, token revocation and recovery. Use
[INTERACTION-SURFACES.md](INTERACTION-SURFACES.md) as the accepted product boundary.

### R3 — PAUSE and cancellation semantics

**Question:** Can user-selectable pause policies let bounded operations finish without
allowing a compromised or disconnected actor to create new effects?

Compare structured cancellation and shutdown semantics in operating systems, workflow
engines, job schedulers and agent harnesses. Model at least `checkpoint`, `interrupt` and
`drain` policies plus an independent emergency stop. Define behavior for a model turn, local
transaction, subprocess, remote/disconnected action, read-only gate, publication and an
ambiguous external effect. Produce a transition/crash matrix and constitutional amendment
options. The current recommendation is `checkpoint` as the normal default, while emergency
stop blocks new effects immediately and quarantines uncertain output.

### R4 — calibrated Full Access

**Question:** How can Full Access be genuinely expansive without becoming silent
self-escalation or unauditable ambient authority?

Research capability systems, privilege separation, just-in-time elevation, break-glass
administration and dangerous-mode UX. Compare a single boolean with a capability vector for
control-plane writes, credential administration, new billing authority, publication, merge,
deployment, service control and audit-policy changes. Specify acknowledgement, authentication,
time bounds, scope, inheritance, revocation and recovery. Test the recommendation that a
`sovereign` preset may explicitly grant every supported capability while no running actor may
mint or conceal its own grant.

### R5 — risk-scaled independent verification

**Question:** Which independence dimensions materially improve defect detection for each risk
class?

Research software-assurance, reproducible-build, safety-case and multi-model evaluation
practice. Compare separation by task, context, session, model, family, provider and host.
Pre-register a blind matrix using exact candidates and deterministic gates. Produce risk tiers,
fallback behavior when independent routes are unavailable, and release-blocking rules. The
starting recommendation is: deterministic-only for purely mechanical evidence; clean separate
session for routine changes; different capable model/family for material changes; different
provider/family plus owner approval and independent execution environment for constitutional,
credential, spending, publication, deployment and release boundaries.

### R6 — plugin signing and unsigned local power

**Question:** What does maintainer approval prove, and how can unsigned local plugins retain
full feature expressiveness without warning-only supply-chain failure?

Research package signing, transparency, lockfiles, SBOMs, reproducible bundles, sandboxing and
capability consent. Separate functional API access from ambient privilege. Test the proposed
compromise: signed plugins can carry a reviewed publisher policy; unsigned plugins may use the
complete plugin API, but sensitive capabilities require a digest-pinned, per-plugin owner
grant and developer-mode step-up rather than one generic warning. Preserve the owner's ability
to override locally without granting a remote maintainer veto.

### R7 — single-writer migration and effect rollback

**Question:** What exact checkpoint is sufficient to fence a legacy writer and transfer one
aggregate to v3?

Research event-sourced stranglers, expand/contract database migrations, sagas/outboxes,
fencing, shadow reads and external-effect reconciliation. Apply them to the verified writer
inventory in [CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md). Produce per-aggregate entry,
cutover, rollback and point-of-no-return gates. The starting recommendation requires no active
lease/open attempt/publication intent, exact import/projection digest parity, tested backup and
reverse reader, a new fencing epoch and one owner-approved low-risk canary aggregate. Provider
submissions, pushed refs, sent messages, credential changes and deployments reconcile forward
once externally accepted.

### R8 — adaptive branch and review-backlog capacity

**Question:** Which measured signals should bound new branches, worktrees and concurrent ARM
output?

Measure Git/worktree operation latency, disk/inodes, process and index overhead, integration
conflicts, stale-branch age, unreviewed change volume and owner review service rate. Distinguish
machine pressure from human review debt. Produce an adaptive admission policy with hysteresis,
an owner-set hard ceiling and safe pruning rules. A large machine must not generate work faster
than evidence can be reviewed merely because branch creation is cheap.

### R9 — privacy-preserving retention and deletion

**Question:** How should raw private artifacts expire while durable lineage remains auditable?

Research cryptographic erasure, physical deletion, tombstones, backup expiry, legal hold,
content-address leakage and per-project keys. Test the recommendation to encrypt raw artifacts
with scoped data-encryption keys, delete expired blobs and keys, and retain a minimal signed
tombstone containing policy/version, class, time and outcome but no recoverable content.
Specify propagation across caches, backups and disconnected nodes, plus owner purge and pin.

### R10 — private canary methodology

**Question:** What can `CANARY-01` prove without leaking its identity or allowing a successful
run to substitute for fault coverage?

Use only local/private eligible routes for real project inspection. Public research receives
synthetic construction-domain fixtures. Define bounded canary tasks, failure injection,
baseline comparison, owner review measures, disclosure boundaries and stop conditions. The
canary does not begin during the research campaign.

### R11 — interactive terminal runtime and communication visualization

**Question:** Which persistent process, client protocol and terminal rendering architecture can
support several detachable Head/ARM/worker views with clean termination and negligible passive
overhead?

Compare Windows ConPTY/Job Objects/Windows Terminal integration; POSIX PTYs, sessions, process
groups and signals; detachable multiplexers; service supervision; mature TUI diff renderers;
IPC authentication; stream cursors; flow control; and agent-CLI multi-session failure modes.
Specify daemon/process-broker/view ownership, attach/detach/reconnect, saved layouts,
configuration transactions, graph-and-stream communication views, non-flicker rendering,
plain-text/accessibility fallback, graceful/forced/emergency termination and orphan detection.
Run or preregister the cross-platform experiments in
[TERMINAL-RUNTIME.md](TERMINAL-RUNTIME.md) and PERF-010. Reject any design where terminal close
kills work, a passive view launches execution, a slow client blocks canonical state, or the
daemon cannot terminate its full descendant process tree.

### R12 — whole-system performance and lean codebase

**Question:** Can v3 materially improve capability while keeping the privileged core and idle
installation small enough to understand, audit and run on the target coordinator?

Establish v2/reference baselines for startup, idle CPU/RSS/wakeups, install/binary/dependency
size, imported modules, daemon/process count, event/replay/WAL behavior, CLI latency and lines or
complexity in privileged versus optional code. Map every mandatory mechanism to one owner and
identify duplicate state, routing, process, context and plugin paths. Compare monolith,
microservice and small-kernel/plugin packaging. Produce hard budgets only after measurement;
remove or isolate features whose benefit does not justify permanent core cost.

### R13 — model performance, routing and delegation science

**Question:** Which models, harnesses, delegation shapes and verifier combinations maximize
accepted outcomes per quota/cost/resource/review unit for each task class?

Build a contamination-aware task corpus spanning planning, architecture, security, backend,
frontend, mechanical work, debugging, integration, documentation and research. Pre-register
quality floors and blind review. Compare one strong ARM, bounded specialist delegation,
multi-ARM collaboration and uncontrolled swarms; task-specific suites versus a universal
ladder; same-route continuity versus checkpoint switching; and strong versus cheap planning.
Measure variance, repair work, false-green gates, owner review and provider/version drift. Do
not publish a universal model ranking from incomparable prompts or one run.

### R14 — context, compaction and cache manipulation

**Question:** Which lawful, documented cache/session/context controls reduce repeated work
without hidden coupling, privacy leakage or fidelity loss?

Separate deterministic stable prompt prefixes, provider-reported cache controls, CLI/provider
session affinity, repository evidence caching, content-addressed artifacts, context capsules,
compaction and lazy hydration. Verify exact route exposure and billing semantics at dated
versions; never infer cache hits or savings. Test same-route and cross-route continuation,
cache invalidation, source changes, repeated compaction, intent recall, private-project
isolation and cold recovery. "Cache manipulation" means supported prompt/layout/session/cache
controls and local evidence reuse, never attempts to bypass provider policy or fabricate usage.

### R15 — configuration architecture and operator control

**Question:** Can one schema make deep customization predictable across files, interactive CLI,
Telegram, editions, goals, tasks, plugins, routes, nodes, PAUSE, Full Access and terminal
layouts?

Research configuration languages, typed schemas, provenance/explain, inheritance, narrowing and
widening, transactional edits, concurrent clients, migrations, validation, secret references,
presets, feature flags and rollback. Test novice setup and expert editing, stale-version
conflicts, partial failure and cross-platform paths. Produce the smallest set of orthogonal
settings; reject combinations whose interactions cannot be explained or tested. Configurability
is not permission to weaken silent integrity invariants.

### R16 — scientific research ARM and scholarly evidence

**Question:** Can Recursion find papers and standards, reconcile conflicting evidence, design
experiments and produce reproducible architecture claims within privacy, copyright and budget
limits?

Research official scholarly metadata/search APIs, persistent identifiers, correction/retraction
signals, full-text licensing, citation graphs, PDF/table extraction, experiment registration and
reproducible analysis. Compare source discovery and synthesis systems using adversarial false
citation, outdated version, paywall, contradictory study and inapplicable-population fixtures.
Specify the lean plugin boundary and evidence objects in
[SCIENTIFIC-RESEARCH.md](SCIENTIFIC-RESEARCH.md). Papers support mechanisms; local structural
and empirical evidence decide Recursion fit.

### R17 — comparative architecture benefit and complexity budget

**Question:** Does v3's additional machinery outperform v2 and simpler alternatives enough to
justify its code, operational and cognitive cost?

Build matched end-to-end scenarios against the verified v2 baseline, Option 1 incremental
extraction, Option 2 kernel/adapters and bounded Option 3 native-loop spikes. Measure the entire
optimization envelope, including owner review and maintenance burden. Require an ablation study:
remove or disable each major subsystem and identify which accepted outcome degrades. Recommend
adopt, simplify, defer or delete. A feature that cannot show a user-visible, safety or measured
efficiency benefit should not become mandatory core.

## Evidence and route separation

Public Deep Research may inspect public standards, papers, official product/API documentation,
public source repositories and licenses. It must not receive unpublished v3 drafts verbatim,
the transcript archive, private project identities/content, local paths, credentials, account
details or infrastructure identifiers. The lead converts local questions into minimal public
or synthetic briefs and verifies consequential sources directly.

Local-only work may inspect the Recursion source, tests and sanitized synthetic fixtures. Live
deployment inspection, provider-auth changes, paid routes, private-canary execution and runtime
implementation require separate authorization.

## Required outputs

1. A source-pinned report for each R1–R17 lane with claim, contradiction, confidence and
   adoption decision.
2. Updated claim ledger with stable IDs and time-sensitive expiry triggers.
3. Native-harness responsibility matrix and falsifiable inner-loop spike.
4. ARM/Telegram topology and message-authority protocol options.
5. PAUSE transition/crash matrix and constitutional amendment alternatives.
6. Full Access capability/grant matrix and threat model.
7. Verifier risk tiers with deterministic and human fallback rules.
8. Plugin trust/signing/developer-mode decision matrix.
9. Per-aggregate migration/cutover/rollback table.
10. Branch-capacity benchmark plan and retention/deletion protocol.
11. Persistent terminal/process architecture, communication-view wireframes and a
    cross-platform non-flicker/resource/termination test plan.
12. `CANARY-01` private runbook using only an alias in tracked docs.
13. Optimization-envelope baseline, model/delegation evaluation, context/cache study,
    configuration contract and core complexity/ablation budget.
14. Scientific Research ARM protocol with scholarly adapter, reproducibility, copyright and
    false-citation gates.
15. Revised v3 specification, open owner decisions and contract-milestone readiness verdict.

## Completion gate

- Every consequential factual claim has a direct primary source or is explicitly unverified.
- Every recommendation has a competing option, failure mode and decisive test.
- Every claimed improvement is compared against v2 or a named simpler baseline across the
  relevant optimization dimensions; no aggregate score hides a failed hard floor.
- Sources are pinned by version/date; licenses and applicability are recorded.
- Owner decisions are not reopened, and proposals are not promoted into owner decisions.
- Current constitutional conflicts are named rather than silently overwritten.
- Public/external research packets pass a privacy scan; private canary identity/content remain
  outside tracked/public artifacts.
- No route listing or successful response is treated as entitlement, privacy or billing proof.
- No runtime implementation, provider/auth change, spending, deployment, service action,
  publication or private canary occurs.
- All documentation changes stay in the separately authorized paths and pass link, secret and
  consistency checks.
- The final report states which questions are empirically resolved, which still require Lucas,
  and whether Milestone 1 is ready.
- Scientific literature is linked through inspectable source records, but no paper or model
  consensus is described as proof of complete local-system fitness without a local experiment.
