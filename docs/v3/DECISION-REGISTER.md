---
title: Recursion v3 decision register and owner queue
status: evidence-reconciled-draft
last-updated: 2026-09-03
source: archive/session-transcript-2026-09-02.md plus owner direction 2026-09-03
---

# Recursion v3 session decision register

## Use and authority

This register consolidates the 2026-09-02 design conversation. It does not amend `CONTROL_PLANE.md` or `state/DECISIONS.md`. `accepted-direction` means Lucas approved the direction in conversation; research may refine mechanics, and constitutional or implementation changes still require their normal review path.

The sanitized transcript preserves exact wording. This register deliberately groups related questions so later agents do not mistake repeated phrasing for separate features.

## Owner rulings and refinements — 2026-09-03

These supersede the matching open questions below. They are v3 product direction. Where a
ruling conflicts with the current `CONTROL_PLANE.md`, it is a proposed constitutional change
until Lucas approves the separate amendment/review workflow; it is not authority for an agent
to change the current deployment.

| ID | Owner direction | Adjudication and remaining research |
|---|---|---|
| OR-001 | Head and ARM planning may use any route in an explicit owner-approved model/provider/account/capacity-pool envelope. | Accepted product direction. Hermes remains the accountable actor; no implicit billing, privacy or authority transition. Requires constitutional reconciliation of the current Codex-OAuth clause. |
| OR-002 | ARMs are goal-scoped delegated executives that plan and delegate a configurable fleet; depth and typical fleet size are configurable. | Accepted. One ARM per repository and delegation depth 1–2 are expected profiles, not protocol invariants. Project Pilot import semantics still require migration proof. |
| OR-003 | `#general` is the Head conversation; each ARM may have a direct Telegram topic so the owner can talk to it without relaying through Head. Investigate GrokBot-inspired macro bots, shared multi-ARM conversations, supervisors and configurable workflows. | Direct ARM conversation is accepted. Head remains aware through canonical events, and chat/topic state is not task authority. Shared-room topology is research, not an accepted design; the exact GrokBot reference must first be identified, and a workflow supervisor may not become an AI ARM Manager. |
| OR-004 | PAUSE aggressiveness is configurable, and normal policy should be able to let an already-started bounded operation finish. | Accepted product direction. `checkpoint`, `interrupt`, `drain` and separate emergency-stop semantics are proposed. Exact effect boundaries require research and a constitutional amendment. |
| OR-005 | Full Access is configurable and may genuinely include control-plane, credential, spending, publication and deployment capability. | Accepted product direction. Recommend an explicit capability vector and maximum `sovereign` preset; no actor may silently self-grant or erase audit. Requires constitutional reconciliation. |
| OR-006 | Verifier independence is a risk-scaled combination. | Accepted. Exact tiers and unavailable-route fallback remain research; current recommendation ranges from deterministic gates to independent family/provider/environment plus owner approval. |
| OR-007 | Maintainer-approved plugins are signed by the trust root. Unsigned local plugins retain full functionality and warn on installation. | Accepted intent. "Full functionality" should mean complete plugin API, while sensitive authority may still require an explicit digest-pinned grant. Warning-only sensitive authority remains disputed pending research. |
| OR-008 | Branch/worktree backlog limits are measured and configurable rather than fixed universally at 75. | Accepted; supersedes 75 as a universal v3 limit. Preserve an owner hard ceiling and human-review-capacity signals. |
| OR-009 | Raw-artifact deletion, cryptographic erasure, tombstone and backup mechanics remain open. | The owner requested a recommendation. Scoped encryption, physical deletion and a minimal signed tombstone are the current proposal; research must reconcile audit continuity with private deletion. |
| OR-010 | The first private canary is an owner-selected construction-domain project. | Accepted as `CANARY-01` in tracked/public docs. Its real identity and content remain private and the canary is not authorized to run by this ruling. |
| OR-011 | V3 is its own optimized harness, initially headless, with CLI rather than a graphical frontend. | Clarified: Recursion owns the orchestration harness even when external optimized inner loops execute turns. Telegram is an optional interactive surface; a complete native inner loop remains a measured expansion. |
| OR-012 | The CLI is interactive and supports several terminal windows/panes for Head, ARMs and executors; closing a terminal must not end the process. | Accepted. The daemon/process broker owns lifetime; terminal clients attach/detach. Communication visualization, configuration UX, cross-platform persistence, non-flicker rendering and reliable termination require focused research. |
| OR-013 | Recursion must conduct its own scientific research, find papers and use evidence to improve architecture and configurability. | Accepted. A research ARM uses ordinary GoalSpec/evidence contracts and scholarly capability plugins. Papers support mechanisms; local source and experiments prove Recursion fit. |

## Accepted directions

| Grill Me | Consolidated ruling | Status |
|---|---|---|
| 1 | Long autonomous runs prioritize workable code quality and subscription conservation; time is secondary. Concurrency follows measured system/provider capacity. The historical unique-unreviewed-branch cap was 75; OR-008 supersedes that number as a universal v3 limit. Task gate failures escalate through the ARM instead of globally pausing; a Lucas-required escalation stops affected development. | accepted-direction, partially superseded by OR-008 |
| 2–3 | On subscription exhaustion, only an already-started bounded final turn may reach a checkpoint. Metered fallback requires prior authority. The proposed `$10` is one aggregate parent-goal budget, never a fresh subtask allowance. | accepted-direction; enforcement needs provider research |
| 4 | Begin with a small number of private, meaningful canary tasks and evidence-based consolidation; successful runs are confidence evidence, not proof of no failures. | accepted-direction |
| 5 | The initial CLI serves Lucas's coordinator deployment and makes files/settings accessible without requiring an agent. OR-012 further requires interactive, detachable multi-window operation. | accepted-direction, extended by OR-012 |
| 6–7 | Model/config changes apply at the next mechanically safe checkpoint; owner-forced swap is available. Atomic operations may reach their bounded boundary; emergency kill is separate. | accepted-direction |
| 8 | Automatic route reordering is allowed only inside an owner-approved envelope; authority, providers, budgets, and permissions cannot widen themselves. | accepted-direction |
| 9 | New routes/models graduate through capability/authentication, synthetic checkpoint/failure fixtures, and a low-risk independently verified canary. | accepted-direction |
| 10 corrected | Routes bind explicit engine/transport, provider, model, and capacity pool. Subscription/OAuth and metered API billing never switch implicitly. Bring-your-own accounts is the public starting posture. | accepted-direction |
| 11–12 | Configuration is hierarchical. Lower scopes may narrow freely; widening spend, credentials, network, permissions, or deployment requires explicit acknowledged authority. | accepted-direction |
| 13 | Full-access and provider-native dangerous permission modes remain configurable. Ordinary trusted autonomy excludes unrelated credentials, control-plane authority, and deployment unless a stronger explicit profile grants them. | accepted-direction |
| 14–16 | Human-readable versioned config is canonical for configuration; CLI is a safe editor/validator. Machine-private config is separated from public source. Project config can propose capabilities but cannot widen the current run. | accepted-direction |
| 17–18 | Raw session retention defaults to 30 days success and 90 days failure, with compact lineage/evidence retained and explicit pinning. Storage classes protect active state and evidence before rebuildable caches. | accepted-direction; legal/deletion mechanics open |
| 19–20 | Worker admission is adaptive to measured resources. Scheduling is goal-aware and fair, allows borrowing, protects interactive use, and supports explicit exclusive goals. | accepted-direction |
| 21–23 | Verification and model suites are task/risk specific. Private deployment defaults to quality-first adaptive routing; all significant quality/cost/reasoning choices remain configurable. | accepted-direction |
| 24–25 | Recursion owns canonical events/checkpoints; provider sessions are disposable affinity accelerators. Explainable local telemetry may reorder only approved routes. | accepted-direction |
| 26–27 | Maintain an auditable downstream Hermes fork: exact upstream base, small compatibility/injection layer, independent Recursion modules, conformance tests, and recorded divergences. | accepted-direction |
| 28–29 | Every segment has an explainable route record. Support `reproduce` and `continue live` replay modes, with live re-admission as autonomous recovery default. | accepted-direction |
| 30–31 | Canonical runtime state is SQLite/WAL plus content-addressed artifacts. Use one lightweight daemon per authority domain/OS account, not one daemon per repository. | accepted-direction |
| 32–33 | Trusted workers default to native Git worktrees plus OS resource isolation; containers are configurable. The daemon brokers opaque references to provider-native credentials and exposes only the selected account. | accepted-direction |
| 34–36 | Model-aware capacity pools use evidence with explicit confidence. `ccusage` is an owner-accepted candidate for an optional reconciliation adapter, not live authority; its current source/license/capabilities still require admission research. Stable lineage identifiers are mandatory across adapters; probabilistic correlation is labeled. | accepted-direction |
| 37 | After private validation, the cross-provider Execution Lineage Contract should become a versioned public interoperability specification. | accepted-direction |
| 38–39 | Repository Evidence Cache is commit-addressed, private, project scoped, and not publicly exported. Every project declares classification and egress, defaulting to private/deny. Grill Me becomes a Recursion-specific planning feature. | accepted-direction |
| 40–42 | Planning may learn effective question ordering but not rewrite intent. It has a configurable sub-budget inside the goal. Plan verification is risk scaled and does not assume paid CI. | accepted-direction |
| 43 revised–45 | Authorized work may treat refusals as typed compatibility/continuity events and escalate them. Cross-family retry is configurable and public-default off; it never widens the GoalSpec or defeats hard local/provider/legal boundaries. | accepted-direction, safety wording normalized |
| 46 | Optional phase reserves protect verification and recovery without generating requests; no reserve creates additional budget. | accepted-direction |
| 47–48 revised | Publication uses explicit provenance states and is mandatory in v3. The earlier v4 split was a typo and is superseded. | accepted-direction |
| 49 | V3 is implemented through independently testable milestones; the complete public contract waits for end-to-end acceptance. | accepted-direction |
| 50–51 | Contributor/training-eligible routes default off for private projects. Model capability and delivery routes are separate objects with distinct quota, privacy, price, cache, and health. | accepted-direction |
| 52–53 | Each task uses an exclusive worktree/branch/scope/gate. Overlap is serialized by integration. Automatic pruning touches only proven merged, superseded, or content-identical branches. | accepted-direction |
| 54 | Release readiness uses scenario and fault coverage rather than a success streak. | accepted-direction |
| 55–57 | GoalSpec is immutable/versioned. Safe checkpoints are mechanically validated. Retries require novelty to prevent repeated quota burn. | accepted-direction |
| 58–60 | Verifiers receive clean evidence without implementer persuasion/private reasoning. Disagreement seeks discriminating evidence, and an explicit evidence hierarchy prevents model claims replacing tests. | accepted-direction |
| 61 | Local verification, remote verification, and resource supervision are independent, configurable capabilities. Unavailable CI is reported, not fabricated as passed. | accepted-direction |
| 62–64 | Remote work uses an authenticated hub-and-spoke fabric, defined disconnect behavior, and configurable resource profiles/regression gates. | accepted-direction |
| 65–70 | Signed parent-goal envelopes authorize bounded descendants. Installation trust root, operator credential, device roles, risk-based step-up, and software-update authority are separated. Properly authenticated owner devices may execute authorized remote commands. | accepted-direction |
| 71–73 revised | Remote enrollment requires only lightweight zero-token preflight; full conformance is a release/optional deep suite. Failure quarantines the affected capability. Successful evidence is cached against trust-relevant hashes. | accepted-direction |
| 74–76 | Owner Sovereignty is explicit. A local egress broker protects project/credential/privacy boundaries. One versioned config schema drives files and CLI controls. | accepted-direction |
| 77–79 | Model-independent Context Capsules contain a non-droppable control kernel plus configurable tiers; nodes transfer manifests first and hydrate lazily. | accepted-direction |
| 80–83 | Hybrid adaptive compaction combines native harness behavior with Recursion state. Fidelity validation and rehydration are mandatory. Owner Intent is non-lossy. Models may request compaction; deterministic governor decides; owner may force it. | accepted-direction |
| 84–88 | Each route has a maintainer-owned Context Capability Descriptor. Runtime conflict degrades conservatively with override. Signed data-only descriptor updates are independent. Compaction has an adaptive model-aware pool and qualification suite that does not tax ordinary users. | accepted-direction |
| 89–92 | Optional subsystems obey a Resource Discipline Contract. One schema drives presets/docs/migrations. Setup wizard and tiered doctor are zero-model on their normal paths; deep checks are explicit. | accepted-direction |
| 93–99 | One codebase ships modular release manifests. A small integrity kernel surrounds lazy capability plugins. Features require admission/provenance review. Plugins support sandboxed/trusted/full access, federated sources, deterministic capability graphs, and typed durable/ephemeral events. | accepted-direction |
| 100–102 | Capability-level circuit breakers contain failures. Resource shedding protects integrity and quality. System defaults use cached OS detection and optional explicit benchmarks, not heavyweight startup calibration. | accepted-direction |
| 103 revised | Develop incrementally but release the complete v3 contract atomically; editions physically omit optional weight without restricting source or capability. | accepted-direction |
| 104 revised | Separate product spec, temporary construction runbook, and future research. A Grok-powered watcher is optional construction infrastructure, not a hard-coded product dependency. | accepted-direction |
| 105 | Ship a stable, scheduler-agnostic Observer Interface; read-only observation is separate from scoped control. | accepted-direction |
| 106–108 | ARM model depth is configurable and multi-objective. Local outcome calibration is explainable, bounded, private, and lightweight. Route decisions remain stable until meaningful checkpoints. | accepted-direction |
| 109–111 | Flat subscriptions use confidence-aware capacity shadow pricing. Configurable phase reservations protect late quality work. Hierarchical admission supports quality-wait, adaptive, throughput, cost-first, and custom policies. | accepted-direction |
| 112 | Goal semantics/authority are frozen into the GoalSpec; safe operational settings may change live and other settings apply at checkpoints/restart according to schema. | accepted-direction |

## Superseded or corrected conclusions

| Item | Preserved reason | Replacement |
|---|---|---|
| Initial Grill Me 10 wording implied a stronger product/provider binding than intended. | Prevent surprise billing and unaudited credentials. | Users freely compose routes; each execution resolves to an explicit transport and pool, and billing transitions require authority. |
| Grill Me 48 proposed moving mandatory publication provenance to v4. | Staging contract maturity reduces risk. | Lucas corrected v4 to v3; publication provenance is mandatory in v3. |
| Grill Me 72 initially made full security conformance a prerequisite to remote use. | Remote execution crosses a serious trust boundary. | Lightweight zero-token enrollment preflight is required; full suite is mandatory for official releases and optional for owners. |
| Grill Me 103 initially proposed staged public minor releases. | Smaller public releases reduce integration risk. | V3 is internally incremental but publicly atomic; release manifests control bloat. |
| Grill Me 104 initially risked making a Grok monitor part of the product. | Unattended construction benefits from independent anomaly monitoring. | Product ships a generic Observer Interface; any Grok sentinel belongs to the temporary construction runbook. |
| Grill Me 113 proposed an Executive Supervisor above an AI ARM Manager. | Deterministic admission and budgets need a clear enforcement layer. | Rejected architecture. Head Hermes directly manages ARM executives; the deterministic kernel enforces both and is not another AI manager. |
| Compatibility-bridge destination for v3. | Incremental migration protects proven v2 behavior. | Destination is a Recursion-owned harness/integration re-foundation; construction remains incremental and evidence gated. |

## Corrected executive boundary

The final session correction is authoritative for this design draft:

```text
Lucas
  -> Main Assistant / Head Hermes
       -> goal-scoped ARM Executive
            -> delegated agents / harness sessions
                 -> gates and independent verifier
       -> deterministic enforcement kernel
  -> review, merge, deploy
```

Head owns strategic goals and ARM lifecycle. ARM owns the implementation plan, delegation, and tactical replanning. Workers own bounded execution. The kernel owns deterministic enforcement. No separate AI ARM Manager exists.

## Open decisions requiring research or Lucas review

1. Exact native Recursion agent-loop boundary versus retained Hermes runtime and external CLI engines.
2. Exact amendment text generalizing the planning-model clause to the owner-approved route envelope while preserving Hermes identity and deterministic actuation.
3. Stable public names and schemas for executives, runs, task nodes, capsules, route leases, and events.
4. Numeric resource/performance budgets for each edition and node class.
5. Exact `CANARY-01` tasks and what can be summarized publicly without recording its private identity.
6. Supported provider/model/CLI matrix at v3 cut; all current availability and subscription claims require primary-source revalidation.
7. Which plugins are mandatory in `core` versus included only in other manifests.
8. License and attribution implications of retaining/forking Hermes and adapting patterns from every reference.
9. Migration and rollback point at which legacy writable stores can be retired.
10. Public Execution Lineage Contract contents after the private canary.
11. Retention/deletion design for append-only evidence and encrypted raw artifacts.
12. Whether Head and ARM use the same native loop implementation or specialized loops behind a shared executive protocol.

## Candidate next foundational research decision

Which parts of the inner agent turn loop should Recursion implement natively while treating
Codex, Cursor, Claude Code, Gemini CLI, OpenCode, Hermes, and similar harnesses as optional peer
execution engines behind the same ARM, context, evidence, terminal and telemetry contracts?

OR-011 establishes that v3 is a Recursion-owned headless harness. It does not require v3 to
reimplement every provider-optimized turn loop. The research campaign recommends a native
deterministic kernel with compatibility adapters, while keeping a complete native inner loop as
a separately measured capability. See [ARCHITECTURE-OPTIONS.md](ARCHITECTURE-OPTIONS.md).

## Research adjudication, 2026-09-03

- V2's packet, placement, recovery and evidence invariants are strong source/test substrate.
  The MVP composition is source-only in the inspected tree; it is not a verified deployed v3
  runtime.
- The operational-path source still spans Head decision/actuator, Project Pilot/reconciler,
  worker, evidence and publisher paths. A new SQLite writer must not coexist as a second writer
  for the same aggregate.
- Public references support concrete event, plugin, compaction, provider-loop and observer
  patterns, but no reference supplies Recursion's authority/evidence/publication lineage.
- Provider/model preflights establish only local route behavior. They do not establish future
  availability, entitlement, privacy, cache portability or free metered usage.
- Grok 4.5 through the requested Codex custom-provider route was unavailable and was omitted,
  reducing cross-family diversity to Luna plus public-only Muse.

These are evidence classifications recorded in [CLAIM-LEDGER.md](CLAIM-LEDGER.md), not owner
decisions.

## Remaining owner decisions after focused research

The broad direction is now answered. Research should narrow these mechanisms before asking
Lucas to ratify them:

1. Exact amendment text for provider-neutral Head/ARM planning while preserving Hermes identity,
   deterministic actuation and explicit billing/privacy envelopes.
2. Whether Project Pilot imports as an `ArmRun` predecessor or only migration evidence.
3. Default PAUSE profile and the exact finish/interrupt/quarantine rule for each effect class.
4. Full Access grant schema, step-up/expiry rules and whether any audit/grant-control capability
   can safely be delegated.
5. Verifier risk tiers and which unavailable-independence conditions block a release.
6. Whether unsigned-plugin installation warning alone can authorize sensitive capabilities or
   a separate digest-pinned developer-mode grant is mandatory.
7. The per-aggregate legacy-writer cutover point and reconciliation-only external effects.
8. Raw-artifact cryptographic erasure, physical deletion, tombstone and backup policy.
9. Safe multi-ARM shared-room topology and whether coordination belongs to Head or a named ARM.
10. Persistent terminal/process architecture and the v3-supported terminal/OS matrix.
11. The exact bounded `CANARY-01` tasks, evidence, disclosure and stop rules.

## Next Grill Me queue after research

1. Do you ratify `checkpoint` as the ordinary PAUSE default, `interrupt` and `drain` as explicit
   alternatives, and emergency stop as a separate immediate boundary?
2. May a maximum Full Access actor ever modify its own grant/audit controls, or may it exercise
   every operational capability while grant issuance and audit deletion remain owner-held?
3. For unsigned local plugins, is the installation warning itself sufficient for requested
   sensitive authority, or should sensitive grants require a second digest-pinned step-up?
4. Which proposed verifier tier should be the minimum for releases when an independent family,
   provider or host is unavailable?
5. In a shared multi-ARM room, should Head always own the coordination lease, or may a named ARM
   own one workflow step under a cross-ARM GoalSpec?
6. Which PAUSE, Full Access, plugin and terminal defaults should ship in `core`, `standard` and
   `full` manifests?
7. Which exact v2 aggregate should undergo the first single-writer cutover rehearsal?
8. Do you accept scoped encryption plus physical deletion and a minimal signed tombstone as the
   default retention design?
9. Which supported Windows/Linux terminals must pass v3.0 interactive acceptance, and should
   OS-native window/pane launching be core or an optional adapter?
10. Which bounded `CANARY-01` task should run first after contract/replay acceptance?
