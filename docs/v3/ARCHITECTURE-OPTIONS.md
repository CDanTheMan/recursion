---
title: Recursion v3 architecture options and recommendation
status: recommendation-with-owner-directions-and-open-proof
last-updated: 2026-09-03
baseline-commit: 98113d6c6d3debe2a4d207c51bb1780f7356d714
---

# Recursion v3 architecture options and recommendation

The options below are intentionally distinct. Scores are qualitative hypotheses grounded in
the current source trace and pinned public mechanisms; they are not benchmarks.

## Option 1 — extract incrementally from the current Hermes-derived runtime

Keep current scripts and file/Git state authoritative. Generalize Project Pilot, adapters and
schemas in place until the system resembles v3.

| Dimension | Assessment |
|---|---|
| Product fit and UX | Fastest path to visible continuity; hardest path to one coherent observer/config model |
| Ownership/upstream | Small initial delta, but Recursion behavior remains distributed across inherited scripts and upstream assumptions |
| Isolation/security | Retains tested fences; continuing duplicate state and dispatch paths complicate global invariants |
| Plugins/context | Easy to add adapters, difficult to guarantee one lifecycle, event order or compaction owner |
| Migration/rollback | Lowest near-term migration risk; high long-term deletion and schema debt |
| VPS/testability | Known thin-client posture; end-to-end deterministic replay remains difficult |

Strongest case: it preserves the widest amount of operational-path source and makes every
change individually reversible. Strongest counterexample: an apparently small cross-cutting
feature such as PAUSE, route attribution or publication must be updated consistently across
many writers and projections. It wins if a write-set audit shows the current system already
has one enforceable transition boundary and v3 needs only surface cleanup.

## Option 2 — native deterministic kernel with compatibility adapters

Build a small Recursion-owned authority/event/action kernel. Keep current loops and external
CLIs as engines behind immutable contracts. Migrate by read adapters, shadow projections and
single-writer cutovers per aggregate.

| Dimension | Assessment |
|---|---|
| Product fit and UX | Best fit for one owner-visible state, explainable routes and durable Head/ARM identity |
| Ownership/upstream | Recursion owns differentiating policy; provider loops remain replaceable and upstream-compatible |
| Isolation/security | Small privileged kernel can fail closed; adapters remain untrusted at the authority boundary |
| Plugins/context | Typed capability graph outside the kernel; provider-native sessions/caches remain route-local accelerators |
| Migration/rollback | Moderate risk, controllable only with one writer per aggregate and explicit compatibility checkpoints |
| VPS/testability | Event-driven coordinator can remain small; pure commands, replay and fake effects are directly testable |

Strongest case: v2 already proves many kernel contracts in source while the operational system
already separates model decisions from deterministic actuation. Public T3 Code independently
demonstrates one-at-a-time command-queue processing and transactional append/projection while
also using separate provider/settlement workers; DeepSeek Harness demonstrates typed replaceable
capability seams with an explicit persistence flush boundary. Neither proves Recursion's migration.

Strongest counterexample: adapters can become a permanent second architecture, and a clean
shadow reader does not test write contention or cross-aggregate consistency. This option loses
if the first replay/conformance milestone cannot express current v2 evidence without lossy
special cases, or if measured compatibility cost is comparable to replacing the inner loops.

## Option 3 — complete native harness; external CLIs as provider plugins

Own the agent turn loop, tools, subagents, terminal/session lifecycle, compaction, checkpoints,
context construction and UI protocol from the start. External CLIs become optional provider-
tuned plugins rather than retained execution loops.

| Dimension | Assessment |
|---|---|
| Product fit and UX | Highest ultimate coherence and control |
| Ownership/upstream | Maximum Recursion ownership; maximum maintenance and provider-specific behavior burden |
| Isolation/security | Can design one boundary, but the new tool/terminal/loop surface greatly expands trusted code |
| Plugins/context | Cleanest theoretical composition; easiest to duplicate mature provider-native optimizations incorrectly |
| Migration/rollback | Highest risk and longest interval before a meaningful compatibility canary |
| VPS/testability | Core may be lightweight, but resident tools/indexers and broad test matrix threaten the small coordinator |

Strongest case: a native turn/event protocol gives portable context, exact lifecycle hooks and a
single operator surface. Strongest counterexample: provider loops encode undocumented streaming,
tool, approval, cache and compaction behavior. Pi and DeepSeek show good loop seams, but do not
remove that replication burden. This option wins only after a bounded inner-loop spike shows a
material quality, continuity or resource advantage that adapters cannot deliver.

## Recommendation

Recommend **Option 2**. Make the deterministic contract/event kernel native now; keep agent
inner loops replaceable through engines; earn any later native loop one bounded capability at a
time. This preserves the accepted custom-harness destination without treating a ground-up loop
rewrite as a prerequisite.

The smallest privileged kernel owns schema versions, authority/budget checks, command
idempotency, event sequencing, action admission, PAUSE epoch, credential-reference policy,
verification identity and publication provenance. It does not choose product goals, write an
ARM plan, select architecture by model opinion or act as an AI ARM Manager. The Recursion Head and
ARM executives propose semantic transitions; the kernel accepts or rejects and actuates only
fixed verbs.

### Recommendation falsifiers

Reverse or narrow this recommendation if any of these is observed:

1. A frozen v2 fixture cannot round-trip through the proposed contracts without losing an
   authority, evidence, publication or retry invariant.
2. The compatibility layer needs provider- or project-specific branches inside the privileged
   kernel rather than outside it.
3. Single-writer cutover cannot be proved because legacy write paths cannot be enumerated or
   fenced.
4. On the target coordinator class, replay/projection or plugin discovery exceeds the measured
   latency, memory, disk or recovery envelope in [PERFORMANCE-PLAN.md](PERFORMANCE-PLAN.md).
5. A native-loop spike materially improves a declared quality/continuity metric at acceptable
   maintenance cost, making a larger share of Option 3 preferable.
6. The existing runtime proves one stable transition boundary with lower total change than the
   adapter/kernel split, making Option 1 sufficient.

### Disabled-path cost commitments

For Option 2 to remain preferable, an unselected engine, provider, node transport, observer,
indexer, contributor route or native-loop spike must perform no model/network call, import no
plugin implementation, hold no worker process, and create no periodic background work. Its
unavoidable cost is limited to bounded manifest metadata used by zero-token capability
resolution. Edition manifests may omit that metadata entirely. These are acceptance
hypotheses, not measured facts; PERF-003 and the `core`-without-external-engines acceptance
scenario decide them.

Rollback is defined per aggregate, not by reinstalling old code: before the first external
effect, restore the last verified source/state checkpoint and fenced writer; after an effect
whose reversal is not proven, retain the new record and reconcile forward under owner policy.
The concrete strangler and stop rules are in
[CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md).

## Constitutional reconciliation requiring Lucas

These are proposed rulings, not decisions. `CONTROL_PLANE.md` remains authoritative.

1. **Planning compute.** Lucas selected provider-neutral Head/ARM compute inside explicit
   owner-approved model/provider/account/pool envelopes. Amend the provider-specific clause
   while preserving the Recursion-owned `Head` as accountable logical executive and
   deterministic actuation. A Hermes implementation may remain a migration/engine adapter.
2. **Executive hierarchy.** Lucas defined ARM as a goal-scoped executive that delegates a
   configurable fleet and may receive direct owner conversation. The Head-to-ARM hierarchy has
   no intervening AI ARM Manager. Whether Project Pilot can import as an ARM predecessor still
   requires compatibility proof.
3. **State authority.** Ratify the future transfer from file/Git operational records to one
   kernel event writer, with human-readable Git projections remaining review artifacts rather
   than concurrent authority.
4. **PAUSE versus checkpoint completion.** Lucas selected `checkpoint` as the future product default,
   with `interrupt`, `drain` and emergency stop explicit. Research must specify their behavior
   per effect class before an amendment replaces the current immediate halt.
5. **Full access.** Lucas selected a genuinely expansive configurable Full Access that may
   include control-plane, credential, spend, publication, merge and deployment capability.
   Maximum `sovereign` may explicitly include `grant-admin` and modify its own grants. Research
   must define receipt-backed mutation, step-up, expiry and the separate audit-retention seam
   before constitutional amendment.
6. **Native inner loop.** Ratify or amend Option 2 as the construction path and require a measured spike
   before promoting a Recursion-owned inner agent loop from optional capability to core.

Publication provenance, no secret values in durable state, non-widening child inheritance and
truthful verification status need no weakening. Merge/deploy/grant administration may move only
through an explicit maximum `sovereign` capability and operative amendment; missing verification
still cannot become a pass. Any amendment should preserve these boundaries.
