# Standalone harness foundation campaign

Date: 2026-09-05. Current status: **resumed after explicit Owner scope ruling**.
Initial status was **blocked at preflight; research not admitted**. The initial evidence
below is preserved. This is not yet a completed research report or accepted product decision.

## Frozen invocation and boundary

The Owner explicitly invoked the complete
[research handoff](../prompts/standalone-harness-foundation-deep-research.md) in the
current private campaign conversation on 2026-09-05. That message is the exact private
intent reference; it is not copied into this publication-safe summary. No earlier
conversation or archived transcript was used.

- Parent: `goal-recursion-v2-execution-fabric`; its record remains active and its
  provider-neutral outcome applies. Its acceptance suite is unchanged.
- GoalSpec: `recursion.v3.foundation.research.20260905`, version 1 as defined by the
  immutable handoff and Owner invocation. No semantic amendment has been accepted.
- Branch: `codex/v3-formal-model-experiment`; existing dedicated registered worktree.
- `start_commit`: `f28f620644115b7d14eeab32f3f2d192034dd8ea`.
- Required merged baseline and fetched `origin/master`:
  `a7cd9458d37f3090079930bf8d79ffd77c4f73e4`.
- Budget: one bounded six-hour session; zero new metered spend; included capacity only;
  at most four concurrent discovery packets, 30 minutes per packet, synthesis/review reserve.
- Sole integrator/writer: Astra. Planned native discovery: four read-only Luna packets,
  medium for extraction and high for invariant/security work. Planned review: eligible
  Cursor Grok 4.6 high/xhigh, otherwise the authorized Terra high fallback, at most two.
  No route was invoked, changed, or independently certified by this preflight.
- Private material stays on admitted private routes. Public queries and optional
  Contributor work receive only independently written public/synthetic questions.
- Allowed changes: `docs/v3/foundation-research/**` and the following files directly
  under `docs/v3/`: README.md, PRODUCT.md, ARCHITECTURE.md, EXECUTIVES.md,
  EXECUTION-FABRIC.md, PLANNING.md, CLI.md, TERMINAL-RUNTIME.md,
  INTERACTION-SURFACES.md, CONTEXT.md, PLUGINS-AND-EDITIONS.md, SECURITY.md,
  TELEMETRY.md, PERFORMANCE-PLAN.md, ACCEPTANCE.md, ROADMAP.md,
  CONSTRUCTION-RUNBOOK.md, DECISION-REGISTER.md, CLAIM-LEDGER.md,
  CLAIM-REGISTRY.json, SOURCE-REGISTER.md, ROUTE-CAPABILITIES.md,
  RESEARCH-HYPOTHESES.md.
- Everything else is read-only. No implementation, provider probe, live effect, setup
  change, benchmark run, PAUSE change, publication, push, merge, or deployment is authorized.

## Input digests

SHA-256 of invocation-worktree bytes, verified before this record was created:

| Input | SHA-256 |
|---|---|
| CONTROL_PLANE.md | `10a1a8bae850880e1829cab7d343e4a4538ff7287fbabbd1a8237da3035c8643` |
| CLAUDE.md | `e2c8bbe7fe665647ae1f773257f13581d6cd53d229a4ec9ff4d72b091cb673d5` |
| ANCHOR.md | `aaf33a7ef097955ea188f79f8149e134485a3d015b09f4ab6c470290fdc757f0` |
| docs/v3/prompts/standalone-harness-foundation-deep-research.md | `22f11fa30cfd98a6e67865d7da916bd7c728a27e8c44f7bd24aed6028bc31e23` |
| state/goals/goal-recursion-v2-execution-fabric.md | `b3f2681b0dd00d2baf0c84f63a7db35576f969ca937d007ac2b519c2518a5970` |

Tracked CLAUDE.md and the invocation-supplied AGENTS.md rules were read. No filesystem
AGENTS.md or additional applicable ancestor/nested instruction file was found. The Deep
Research and OpenAI Docs skills were read. No `update_plan` tool is exposed in this
session; the campaign record is the available durable planning/checkpoint surface.

## Preflight evidence and blocker

Checks completed by 2026-09-05T09:07:37Z:

| Check | Result and limitation |
|---|---|
| Git | Clean target; exact expected branch/HEAD; worktree registered once; no index lock. No conflicting active target session appeared in the app listing; that listing cannot prove an exclusive OS lock. |
| Remote/ancestry | `git fetch origin master` succeeded. The WIP branch contains two prompt-only commits above the required baseline. No reset/rebase/merge/stash/clean/prune/switch occurred. |
| M1 ancestry | All six implementation/receipt commits named in the handoff are ancestors of start_commit. Implementation-byte and receipt-digest comparison remains pending; ancestry is not a regression rerun. |
| Local PAUSE | Absent in target and original main checkout. Neither absence establishes operational state. |
| Operational PAUSE | **Present**, independently read over the existing noninteractive SSH route. Sentinel timestamp: 2026-09-02T21:38:09Z; reason describes a closed supervised canary window. No local-research exception was recorded in the sentinel. Exact infrastructure locator and raw reason remain in private preflight tool provenance. |
| Capacity | About 34.5 GiB free physical memory and 641 GiB free disk; shell/retrieval commands responsive. CPU utilization is unavailable: the first counter was null and the performance-counter class query failed. No numerical CPU headroom claim is made. |
| Included quota | Read-only account tool reported 36% used in the exposed weekly Codex window, hence 64% remaining; other counters were unavailable. No reset credit or metered route was used. Snapshot is private account evidence, not product entitlement. |
| Tools | Git, Python 3.12.10, Git Bash 5.2.37, rg and SSH available. Cursor Agent help exposes read-only modes, but exact Grok route, effort, included pool and private-data eligibility remain unverified. Native Luna/Terra are exposed by collaboration tooling but were not dispatched. |

Blocker `blocker.foundation.operational-pause` belongs to this GoalSpec and parent goal.
Required actor: Owner for an explicit scope ruling, or the authorized operational owner
for clearance. Under [CONTROL_PLANE.md](../../../CONTROL_PLANE.md#pause), PAUSE halts
planning/workers while preserving durable awareness. The handoff explicitly requires
checking known operational PAUSE and following its operative rules. Whether an isolated
local documentation campaign may proceed despite that sentinel is not assumed here.

Resume action: record an explicit Owner ruling that this bounded local research may
proceed while operational PAUSE remains present, or obtain operational clearance; then
rerun changed preflight checks and finish route/capacity admission. Do not request the
same general campaign authorization again or clear PAUSE from this session. Append the
ruling and disposition; preserve this failed admission evidence.

## Task DAG, outputs and remaining gates

| Node | Dependency | Inspectable output/gate | Status |
|---|---|---|---|
| task.foundation.preflight | Owner invocation | This record; all admission prerequisites satisfied | blocked |
| task.foundation.coverage | preflight | Existing-evidence/Owner-thought gap matrix with complete idea coverage | pending |
| task.foundation.discovery | coverage | Bounded read-only packets; opened primary sources and provenance | pending |
| task.foundation.reconcile | discovery | Source verification, contradictions, freshness and dissent dispositions | pending |
| task.foundation.synthesis | reconcile | Canonical updates, evidence.json, compatibility.json, experiments.json, decisions.json, synthesis.md and grillme.md | pending |
| task.foundation.gates | synthesis | check.py; exact clean candidate gates twice; fresh M1A/M1B/M1C and v2 receipt commands | pending |
| task.foundation.review | gates | Independent review of identical full candidate hash; repair/re-review if necessary | pending |
| task.foundation.report | review | Verdict, commit hashes, evidence gaps and first pending GRILLME decision | pending |

Expected artifacts and machine-checkable definitions remain exactly those in the handoff.
The future terminal command is `python -B docs/v3/foundation-research/check.py --base
<start_commit> --candidate <full-candidate-sha>`, twice on the identical clean candidate.
That checker has not been created or run. Existing regressions and independent review
have not run. This blocked record is not a terminal research candidate or an attestation.
Its commit and output digest are reported outside the committed bytes to avoid a
self-referential receipt.

Falsifiers/stop conditions: PAUSE, conflicting target ownership, unrelated dirty work,
missing parent/ancestor, privacy or quota ineligibility, unavailable mandatory verification,
out-of-allowlist changes, fabricated source/status, or an unaccepted authority/goal change.
No foundation verdict, technical correction, experiment result or Owner answer is inferred.
Preserve formal model -> language comparison -> storage comparison; OR-015 remains blocked.

## Append-only PlanRevisions

`plan.foundation.1`, 2026-09-05: preflight only. Retained: immutable Owner invocation,
handoff, parent and Git evidence. Invalidated: assumption that local PAUSE absence could
admit this campaign without resolving the known operational sentinel. Quarantined: no
research output exists. Superseded: none. Stopped before substantive discovery, delegation,
canonical synthesis or experiment design. Resume from task.foundation.preflight.

`plan.foundation.2`, 2026-09-05: Owner explicitly clarified in the current private
conversation that this agent researches/develops the repository rather than operating
Recursion and that operational restrictions do not apply to this campaign. This is the
binding scope ruling for `blocker.foundation.operational-pause`; the blocker is resolved.
Retained: the campaign GoalSpec, research-only allowlist, six-hour/zero-new-spend envelope,
all preflight observations, current operational authority and live-system non-goals.
Invalidated: applying the operational sentinel as an admission block to this isolated
repository campaign. Quarantined: none. Superseded: the stopped admission disposition in
plan.foundation.1, preserved above and in checkpoint commit
`9266020f8907610d06026677b2a05db87f5c69f6`. No operational PAUSE/configuration is changed.
Continue existing-evidence coverage, bounded discovery, synthesis and exact review.

## PlanRevision 3 — completed discovery and source reconciliation

`plan.foundation.3`, 2026-09-05. Retained: GoalSpec version 1, frozen start, accepted architecture,
formal-model/language/storage sequence, all completed M1 work and Owner scope ruling. Superseded:
initial pending discovery and byte-verification statuses in the historical preflight table.
Invalidated: any general inference that observed tool events imply complete effect control;
any blanket Claude subscription-hosting prohibition; universal cache TTL/discount and universal
OpenCode leadership claims. Quarantined: performance, market, route-runtime and Meta-identity
claims without decisive evidence. No product policy or Owner answer is invented.

Additional Owner steering in the same private conversation explicitly emphasizes native
standalone behavior and behavior above upstream harnesses, with Recursion CLI interaction over
Claude Code where authentication requires that route. This clarifies the existing C/F lanes;
it does not amend scope or authorize implementation. It is covered by
`thought.c.claude-layer`, the ownership/capability matrix and the adapter experiment.

Session admission/preflight completed by 2026-09-05T09:07:37Z; the conservative six-hour cutoff
is 2026-09-05T15:07:37Z. No new metered spend, configuration/auth/model changes or live probes
were made. Local Git history retains both admission checkpoints:
`9266020f8907610d06026677b2a05db87f5c69f6` and
`c2c84fa62aa5ce682c3e701c47380c5f167d20de`.

## Discovery WorkPackets and integration

Common packet boundary: parent and GoalSpec above; plan.foundation.2; frozen start
`f28f620644115b7d14eeab32f3f2d192034dd8ea`; discovery checkout
`c2c84fa62aa5ce682c3e701c47380c5f167d20de`; required merged baseline and all six M1
candidate/receipt ancestors. Dependency: preflight and lane-specific coverage map.
Inputs: immutable handoff/authority digests above, canonical paths below, pinned public sources.
Read-only private repository input was admitted through native collaboration; public queries
used generic independently written text, never private paths, hashes, messages or infrastructure.
No shared writes, nested agents, provider trials, credential reads, account login or extra routes.
Time cap: thirty minutes per packet, included capacity only; no separate token budget was
specified. Each returned source/claim/path/version/confidence/contradiction/gap/stop evidence.
Stop on scope ambiguity, privacy uncertainty, missing required input or exhausted budget.
Astra alone consumed, verified, integrated and wrote.

| Packet | Native route | Allowed lane inputs | Output and falsifier | Result |
|---|---|---|---|---|
| task.foundation.harness | Luna medium | SOURCE-REGISTER, REFERENCE-MATRIX, frontier evidence; generic public harness sources | Identity/license/version/benchmark inventory; invented product, unverified ranking or source continuity falsifies claim | completed read-only; lead closed Grok pin and dynamic benchmark gap; Meta referent retained ambiguous |
| task.foundation.engines | Luna medium | ARCHITECTURE, EXECUTION-FABRIC, CLI, route/terminal/plugin docs; official interfaces | Capability/auth/ownership distinctions; missing coverage prevents governed-route claim | completed read-only; focused legal/source-pin correction retained |
| task.foundation.context | Luna medium | CONTEXT, TELEMETRY, PERFORMANCE-PLAN, EXECUTIVES; provider docs/original papers | Cache/compaction/role economics and controls; unsupported price/TTL/performance claim rejected | completed read-only; current Astra threshold and publication-date corrections verified by lead |
| task.foundation.invariants | Luna high | M1 contracts, schemas/pure oracles/tests/receipts; existing formal evidence | Ancestry/bytes/manifest audit and six cross-contract obligations; stale fence, ambiguous retry or false runtime inference falsifies readiness | completed read-only; no M1 edits |

Additional frozen research-input SHA-256 digests at discovery:
- SOURCE-REGISTER.md: `ce145777f219290291ea5abfc97c26152a5d686c8e2bb436a0fcbff216e49353`.
- REFERENCE-MATRIX.md: `1af578a99fcde0bb268428560131dfd5445f6243b4de272eae4484630bca5a61`.
- FRONTIER-HARNESS-EVIDENCE.md: `b18a64ba5331b8292f15b4102bfff84517c1bba58b52489564bbe762573c9aa1`.
- FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md:
  `e45c7ad095643bd4e4d9c8f41943f3cdd945c64c4745944de7b4e60ea1d3b73e`.

No fifth discovery lane was justified: outputs converged and remaining uncertainty requires
separately authorized experiments. Historical same-family M1 reviews and failed candidates
remain untouched. Material disagreements and their resolutions are in evidence.json.

## Candidate preparation and acceptance procedure

Coverage/discovery/reconciliation/synthesis outputs are now in evidence.json (66 thought
dispositions, 18 appended global claims, 32 appended canonical sources), compatibility.json
(14 route profiles, 17 capability dimensions), experiments.json (eight not-run designs),
decisions.json and grillme.md (ten pending answers). Canonical additions are explicitly proposed
where they introduce product policy. Git evidence corrects M1 status to merged without changing
its evidence boundary.

Baseline regressions ran freshly on clean
`c2c84fa62aa5ce682c3e701c47380c5f167d20de`: all planning/execution/integrity schema,
fixture, conformance, adversarial/static and additional planning gates passed; v2 umbrella passed.
The final documentation checker also invokes the separate planning validate-only entrypoint
and all suites again, so its exact final candidate has fresh evidence. Commands and output digests
are emitted as JSON; baseline records and candidate artifact digests are in validation-manifest.json.

Run from the dedicated worktree:

```text
python -B docs/v3/foundation-research/check.py --base f28f620644115b7d14eeab32f3f2d192034dd8ea --candidate <full-candidate-sha>
```

The checker adapts VALIDATION.md without editing it. It includes strict record definitions,
complete diff/ancestry/cleanliness, registry/source/coverage/reference/anchor checks, privacy
patterns, artifact digests and fresh regressions. Its internal adversarial checks exercise
closed fields, duplicate JSON, missing thought coverage, forged observations and invalid references.
Automated structure is not scientific truth or a full privacy certification.

Two successful runs and independent review must bind the identical clean commit. Exact final
attestations stay in the review/tool channel to avoid self-reference; this committed procedure
does not claim a future pass. Any repair or receipt commit requires both gates and exact review again.

Reviewer allocation: Cursor Agent is installed, but the exact Grok 4.6 high/xhigh configuration,
private-data eligibility and included pool could not be verified through the admitted read-only
surface. Do not invoke or reconfigure that route. Use the explicitly authorized native Terra high
fallback, up to two independent read-only reviewers, with no discovery-worker terminal review.
They receive the exact candidate, frozen scope and artifacts plus canonical/private inputs.
Review output must bind candidate, route/effort, independence, findings/severity, decisive checks
and limitations. Separate context/model-role review provides procedural independence but not
external-provider or GPT-family independence. No Contributor route was needed.

Remaining product/evidence gaps: exact Meta referent and several package/binary contracts;
resource-level effect mediation and command fidelity; endpoint-specific counter normalization and subscription debit;
formal refinement, performance, security, user demand and enterprise isolation. All eight designs
remain not run and all ten Owner answers remain pending. Proceed to exact-candidate gates/review;
if the budget expires, preserve an explicitly incomplete checkpoint instead of claiming completion.
