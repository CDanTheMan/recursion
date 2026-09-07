# Architecture comparisons and implementation/research roadmap

2026-09-06. Recommendation: retain the small deterministic kernel and Recursion canonical
ownership, while requiring native, upstream and mixed workflows in the release contract.
The mechanism comparisons below are research proposals. None selects a language, physical store
or a new current authority hierarchy.

## Compare reuse, adaptation and new implementation

| Decision | Reuse | Adapt | New implementation | Discriminating gate |
|---|---|---|---|---|
| Kernel/replay | M1A pure semantics and literal vectors | Project M1A into M1C identities and effect outcomes | New reducer only if equivalent and measurable | E-FHAR2-101 then identical language-neutral vectors; no stale writer acceptance |
| Workflow execution | Existing deterministic fabric primitives | Optional Temporal/DBOS-style workflow executor behind Recursion admission | Small scheduler/timers and persisted work DAG | Task identity export/recovery, ambiguous effects, idle overhead, upgrade/removal rehearsal |
| Native loop | Client libraries/tool protocol implementations | Existing loop component with Recursion-owned lifecycle and accounting | Minimal sampler/tool/context loop | Native-only required scenarios and controls; privileged-code and maintenance cost |
| Upstream integration | Official server/SDK/ACP/headless interfaces | Supported hooks/plugins/MCP plus typed adapter | New adapter where required, not an undocumented credential bridge | Capability composition across all ten controls and upstream-only roles |
| Configuration | Existing schema/resolver semantics | Constraint compiler such as CUE, or validated schema plus semantic rules | Purpose-built resolver only with demonstrated gaps | Conflict explanations, attenuation, deterministic snapshots, startup size and migration cost |
| Plugin runtime | Pinned libraries and bounded subprocess protocol | WASI/WIT component boundary where ecosystem and host support fit | Custom ABI only when concrete coverage justifies maintenance | Same config/behavior on native/upstream, disabled cost, resource containment, version update |
| Storage | Existing durable JSONL primitives + CAS | Single-writer SQLite WAL metadata + same CAS | New store excluded without counterexample | Full-store crash/recovery and growth comparison after language vectors |

[Temporal](https://docs.temporal.io/workflow-execution) documents command/history replay.
[DBOS](https://docs.dbos.dev/python/programming-guide) documents persisted workflow/step state
with SQLite by default and recommends Postgres for production. Those mechanisms warrant
comparison; neither proves Recursion effect certainty or justifies a database decision now.
Keep framework runtime/deployment/license/version costs in the comparison. A dependency's own
workflow history may be an implementation detail only if Recursion's accepted state remains
exportable and recoverable under its release contract.

[CUE](https://cuelang.org/docs/concept/how-cue-enables-data-validation/) offers constraint
unification; this suggests separating hard ceilings from ordinary defaults. It does not decide
scope precedence or who may authorize widening. [WASI](https://wasi.dev/) offers capability-based
component interfaces; host imports remain an enforcement responsibility. Neither is selected.
Source details and limitations are in [integration.json](integration.json).

## Innovation queue with mechanisms and falsifiers

| Candidate | Mechanism and existing Recursion extension point | Experiment / value test | Disposition |
|---|---|---|---|
| Portable continuation contract | Manifest of canonical task/config/evidence plus optional engine-session affinity, extending ContextCapsule and remote attempts | Trial continuity/remote: restore without original session; reject stale artifact/grant; measure rework and transfer | Early interface; exact format proposed |
| Evidence-linked context | Summary assertions retain source/version/locator and supersession edges; extend capsule fidelity and repository evidence cache | Trial continuity: rare constraint/negation/stale-source tests plus retrieval/review cost | Release baseline; advanced policies later |
| Executable capability certificates | Version/config/host-specific observed interaction traces and negative tests; extend M1B route descriptors | Trial integration: schema-compatible behavior drift fails admission; measure certification upkeep | Early interface and release gates |
| Configuration rehearsal | Compile proposed config against actual capability graph and synthetic fault/event traces before activation | Trial configuration: catch incompatible engine/plugin/billing choices without running them | Release setup/update minimum |
| Replaceable effect interfaces | Clock, storage, transport, process and provider I/O behind deterministic test seams | Trial simulation: reproduce seed and minimized counterexample, then validate on real OS adapters | Early seams; deeper simulation later |
| Deterministic infrastructure simulation | Seeded event order, clock, disk/network faults extending M1 replay and reference oracles | Trial simulation plus remote real-host test: find missed interleavings, avoid simulation-only conclusions | Design early; implementation after ordered comparisons |
| Capability-preserving plugin bundle | One semantic config with native and upstream plugin implementations plus explicit loss map | Trial configuration/integration: same command and context behavior, changed engine, disabled plugin | Release mechanism candidate |
| Whole-workflow resource planner | Reserve foreground/verification/recovery capacity across roles and shared pools; extend placement/accounting | Trial performance: direct/single/simple/multi-agent factorial with equal total budgets | Release baseline; adaptive policies later |
| Incremental invalidation graph | Recompute only evidence affected by commit/config/tool changes; extend source/claim and artifact references | Trial continuity: stale evidence trap vs full reinvestigation; total reads/writes/review | Later optimization with early version edges |
| Session-affinity scheduling | Reuse eligible warm process/session only while privacy/config/grants still match; extend route epochs | Trial performance/continuity: warm reuse x compaction x concurrency; compare cold restart | Later tuning; no periodic model keepalive default |

FoundationDB's original [systems paper](https://sigmodrecord.org/publications/sigmodRecord/2203/pdfs/08_fdb-zhou.pdf)
describes seeded deterministic simulation of process, network and disk failures. Borrowing test
seams is a concrete research direction; adopting its database or claiming its reliability is not
a consequence. Newer brainstorming papers (including Cordis and context-compaction theory)
remain discovery leads until identity, content, assumptions and implementation relevance are
verified. Also revisit the existing DeepSeek, Hermes, T3, Grok and Muse source pins for mechanisms
these candidates miss; do not claim that this preparation exhausted the literature.

## Ordered milestones

| Stage | Required work and outcome | What can progress independently |
|---|---|---|
| P0: mapping and source triage | This preparation: accepted Owner requirements, repository map, proposed contracts, traceable next research and trials | No runtime or integration certification |
| P1: integration evidence | Pin eligible routes; small isolated probes of role closure, controls, extensions, config and effect mediation; record failures | Public source/reuse research and fixture design |
| P2: bounded formal model | E-FHAR2-101 with M1 identity/epoch/fence/PAUSE/ambiguity obligations and explicit bounded flow; Owner model/broker choice pending | Further source review, no fixed production runtime assumptions |
| P3: language comparison | Same model-derived neutral vectors and fault workload in CPython/Rust/Go, full optimization vector | Adapter protocol/schema drafts |
| P4: storage comparison | JSONL/CAS versus SQLite-WAL/CAS; disk growth, torn writes, long readers, restart and artifact integrity | CLI rendering/layout investigation |
| P5: shared runtime construction | Canonical writer, admission, deterministic scheduling/accounting, broker, effect reconciliation, recovery and stable control interface | Optional adapters built against frozen contracts under bounded tasks |
| P6: two independently usable pipelines | Small native loop and at least one certified upstream route; all required roles/config/plugins; combined workflow continuity | Additional engines certified on same suite |
| P7: first usable release | Ten terminal controls, setup/import/repair, plugin baseline, compaction, Windows/Linux remote recovery, tested updates, four scenarios | Developer validation; additional OS evidence |
| P8: measured expansion | Wider engine/version/plugin support, advanced context/routing, GPU/approved-cloud profiles, richer supervisor configurations | Admit each by capability and total-workflow measurement |
| P9: later products/infrastructure | Dedicated graphical app; enterprise identity/tenancy/HA; separately justified distributed model inference | Independent evidence and explicit milestones |

The first usable release includes all required behavior at P7 even if earlier internal prototypes
are smaller. Editions may omit unused components; an upstream-only edition cannot omit required
supervision by secretly depending on a native model connection. The exact minimum certified
engine set and public support window remain proposed, not narrowed by this milestone table.

## Decision packet after evidence

1. Model/broker split: smallest canonical aggregate plus separate broker refinement proof, or
   bounded broker state inside the first model. Preserve abstract flow bounds in either case.
2. Certified engine set: select from measured capability coverage, eligible distribution and
   maintenance cost; do not select solely by benchmark ranking.
3. Configuration conflict model: explicit template compilation plus intersected ceilings versus
   a richer constraint solver; compare explanations and dependency overhead.
4. Upstream-only verifier class: determine which workflows can use clean same-engine verification,
   and which require an explicit unavailable-independence outcome under the existing policy.
5. Update guarantee: current plus prior certified build is a proposal; state restore and active-task
   compatibility need concrete evidence before a support promise.

Owner answers remain pending for these implementation choices. Responsiveness/subscription/task
completion priorities guide proposed defaults; material tradeoffs remain visible for decision.
