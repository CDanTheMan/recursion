---
title: Recursion v3 frontier harness research — tranche two evidence
status: evidence-reconciled-draft
last-updated: 2026-09-03
campaign-id: FHAR2-20260903
---

# Frontier harness research — tranche two evidence

This artifact preserves the concise evidence and conclusions returned by the eight Luna discovery
lanes and the Sol lead's direct source reinspection. It contains no private reasoning transcript.
It is architecture and experiment evidence, not a runtime, benchmark result, language selection or
claim that Recursion is already frontier defining.

## Evidence classes and corrections

- **Directly reverified:** Sol opened the cited primary specification, official documentation,
  immutable repository revision or original paper and checked that the narrow claim fits it.
- **Repository-local inference:** a Recursion design conclusion drawn from sources and current
  contracts; sources do not grant Recursion authority or prove the conclusion.
- **Owner decision:** `OR-018`–`OR-020`; these choose direction but do not prove performance.
- **Unverified hypothesis:** requires the stated executable experiment.
- **Worker assertion corrected by Sol:** the initial Cosign packet abbreviated an invalid full
  commit. Tag `v3.1.3` is an annotated tag whose verified target is
  `11926fa5bbbbde47e88fc006b625a17769b743b2`; only that target is used below. The failed pin is not
  evidence.

## Worker disposition

| Packet | Exact route | Question and outcome | Confidence / remaining limit |
|---|---|---|---|
| `WP-FHAR2-101-R` | `gpt-5.6-luna`, `xhigh` | Define the smallest formal transition system capable of falsifying the Option 2 command/event/lease/PAUSE/effect/replay contract. Returned variables, 17 invariants, bounded state, refinement boundary, mutation set and counterexample receipt. | High for modeling method; no TLC run or implementation refinement exists. |
| `WP-FHAR2-102-R` | `gpt-5.6-luna`, `xhigh` | Define an implementation-neutral kernel API and matched CPython/Rust/Go experiment. No language winner selected. | High for comparison controls; performance and maintenance results unmeasured. |
| `WP-FHAR2-103-R` | `gpt-5.6-luna`, `xhigh` | Compare JSONL, SQLite and content-addressed storage plus IPC durability/backpressure. Storage is not authority. | High for primitive semantics; medium for proposed profile; platform results unmeasured. |
| `WP-FHAR2-104-R` | `gpt-5.6-luna`, `xhigh` | Specify Windows/Linux process containment, PTY/ConPTY, reconnect, cursor, lease, flow, rendering and accessibility tests. One partial return received one bounded evidence retry. | High for cited primitives; medium for protocol; native matrix remains unexecuted. |
| `WP-FHAR2-105-R` | `gpt-5.6-luna`, `xhigh` | Define plugin artifact identity, trust/isolation, lifecycle, revocation, grants, frontend bridge and disabled-path tests. | High for source mechanisms; medium for local contract; sandbox efficacy unproved. |
| `WP-FHAR2-106-R` | `gpt-5.6-luna`, `xhigh` | Separate canonical context from route-local caches and define cache/token/fidelity experiments. An initially local-only packet received one bounded source supplement. | High for current API controls; medium for capsule; provider behavior expires quickly. |
| `WP-FHAR2-107-R` | `gpt-5.6-luna`, `xhigh` | Audit corpus, oracle, contamination, statistical unit, human review and stopping rules. Found the existing power claim invalid. | High for the counting defect; sample size awaits blinded calibration/simulation. |
| `WP-FHAR2-108-R` | `gpt-5.6-luna`, `xhigh` | Minimize release identity, cold boot/recovery, dependencies, SBOM/reproducibility and Hermes migration/removal. | High for integrity boundaries; medium for packaging; numeric budgets unmeasured. |

All workers were read-only, made no repository/configuration/provider changes and spawned no nested
agents. Terra dispositions are appended by the campaign artifact after review of an exact commit.

## E-FHAR2-101 — formal kernel model

**Question.** What finite transition system can falsify the ratified architecture before code?

**Direct evidence.** `SRC-V3-095` establishes that TLA+/PlusCal describes initial conditions,
next-state relations, invariants and explicitly qualified liveness/fairness, and that TLC checks a
finite model. `SRC-V3-104` supplies the fencing-token precedent: a session/lease epoch must reach
the resource being protected, not merely the coordinator.

**Repository-local contract.** The model has one canonical aggregate and variables for goal epoch,
accepted GoalSpec digest, plan revision/DAG, task states, packet digests, command IDs, append-only
events, executive/worker/verifier leases and epochs, effect intents/receipts/ambiguity, PAUSE
epoch/mode, retry novelty/attempts, verifier decisions, publication state and logical time. Initial
state is empty and paused only when the operative fixture says so. `Next` is the disjunction of
authenticated acceptance/amendment, plan proposal/admission, task/packet admission, lease
grant/replace/expire, start/checkpoint/complete, gate decision, novel retry, replan/escalate,
effect prepare/dispatch/receipt/quarantine, PAUSE/resume and replay/recovery actions.

The required invariants are:

1. `TypeOK` and closed enum/version domains.
2. `ChainIntegrity` and `AtomicAppend` for event sequence, previous digest and transaction group.
3. `CommandIdempotence`: one command identity has one canonical outcome.
4. `AuthorityScope`: no descendant widens owner, paths, capabilities, privacy, routes or budgets.
5. `LeaseFence`: stale holder/epoch cannot authorize a transition.
6. `AmendmentFence`: a new GoalSpec/plan epoch cannot execute stale packets or effects.
7. `PauseSafety`: forbidden admissions/effect dispatch never occur under the operative PAUSE mode.
8. `RetrySafety`: no retry without failure, remaining bound and canonical novelty evidence.
9. `CancelNoResurrection`: cancelled/superseded work cannot become ready/running/complete.
10. `EffectSafety`: an effect intent precedes dispatch; ambiguous outcome is never success; an
    unproven non-idempotent effect is never blindly repeated.
11. `VerifierSafety`: verifier cannot mutate the plan and missing/downgraded assurance is not full.
12. `ReplayDeterminism`, `ReplayFailClosed` and `ProjectionParity`.
13. `FlowBound`: every queue/retention boundary has a defined block/drop/reset disposition.
14. `NoBlindEffectReplay` after crash, gap or unknown outcome.

Bound the first model to one aggregate, one task/effect/timer/verifier, two workers, two goal epochs,
two plan revisions, three lease epochs, two attempts, an event bound of 20 and small bounded queues.
Then expand only after mutation coverage. Delete or weaken each fence, epoch, novelty, PAUSE and
effect guard in turn; every mutant must yield a retained minimal counterexample containing model
revision/tool version/config, seed, invariant, trace, final state, expected violation and digest.
Liveness is checked only under named weak/strong fairness and explicit environment assumptions;
provider response, owner action and network recovery are never assumed unconditionally.

**Contradiction.** A passing finite model does not prove the unbounded model, the refinement to
code, operating-system containment or external-effect truth. State-space explosion may also hide
an omitted dimension.

**Decision.** Adopt the safety model and mutation receipt as a pre-code experiment. Competing
option: property tests only. Failure mode: the abstract model omits the same race as the code.
Decisive falsifier: a required invariant cannot be expressed without smuggling semantic model
judgment into the kernel, or a deliberately fence-free mutant passes.

## E-FHAR2-102 — privileged kernel API and language experiment

**Question.** Which behavior belongs in the privileged kernel, and how can a language be chosen
without reputation-based guessing?

**Repository-local contract.** The minimal candidate privileged public API is initially:

```text
decode(bytes, schema_epoch) -> closed typed command | typed refusal
admit(immutable_state, expected_state_digest, command, authority/policy fixtures)
  -> accepted event batch | typed refusal
reduce(state, ordered_event) -> state
derive_work_packet(state, admitted_task_id) -> immutable packet | typed refusal
```

`admit` first canonicalizes and verifies `immutable_state` against `expected_state_digest`, then
uses that state—not the digest as a data substitute—for command/receipt/idempotence, GoalSpec,
lease, PAUSE, budget and cross-record checks. These functions receive logical time and random
values only as admitted inputs. They perform no
filesystem, network, process, provider, terminal, plugin, credential or wall-clock access. State
storage, IPC, engines and views call the boundary; they do not move into it.

**Experiment.** Implement the identical API and frozen vectors in CPython, Rust and Go. Required
workload: one GoalSpec, 10 plan revisions, 1,000 tasks, 3,000 edges and 10,000 events; scale check:
10 goals, 10,000 tasks and 100,000 events. Run 5 cold builds, 10 warm builds, 30 cold executions,
100 warm executions and each injected fault three times on pinned Windows and Linux hosts. Measure
bit-identical vectors/digests/refusals first, then build reproducibility, offline dependency
closure, SBOM/license completeness, binary/install size, cold/warm latency, p50/p95/p99 replay,
CPU/RSS/I/O, review time, privileged LOC, dependency graph and fault diagnosis. Use the canonical
Pareto rule; no composite score hides a hard-floor failure.

**Direct evidence.** `SRC-V3-082`–`SRC-V3-086` establish candidate mechanisms and measurement
principles, not a winner. `SRC-V3-105` establishes that a reproducible build is bit-for-bit output
from declared source, environment and instructions. `SRC-V3-106` supplies a normative SBOM
representation; it does not prove semantic safety.

**Decision.** Adopt the neutral API and experiment; defer language selection. Competing option:
continue the existing language without comparison. Failure mode: the benchmark rewards a toy hot
loop while hiding dependency/review and cold-start costs. Falsifier: vector mismatch or a hard
authority/safety/privacy failure eliminates a candidate before performance comparison.

## E-FHAR2-103 — log, projection, artifact and IPC profile

**Question.** Which storage and IPC primitives preserve replay and recovery without becoming a
second authority system?

**Direct evidence.** `SRC-V3-001`–`003` establish SQLite's database-level serialization and WAL
trade-offs, not Recursion fencing. `SRC-V3-007` supplies canonical JSON. POSIX `fsync`/`rename`,
Windows `FlushFileBuffers`/`ReplaceFileW`, RFC 7464 framing, bounded-channel sources and Git's
content-addressed precedent support individual mechanisms only; actual filesystem/runtime behavior
must be pinned and fault tested.

**Candidate contract.** Every frame carries protocol/schema version, aggregate ID, monotonically
increasing sequence, writer epoch, previous digest, payload digest, transaction group and CRC/length.
Canonical JSON uses JCS. Large immutable payloads live in a content-addressed store whose digest is
committed by the event. A projection records source high-water and digest and is disposable. IPC
uses length- or RS-delimited frames with maximum size, version/capability handshake, request ID,
actor/lease/epoch binding, ACK cursor and byte/event credit. A full reader is disconnected or reset;
it cannot block the canonical writer indefinitely.

Compare append-only JSONL/JSON-sequence plus CAS with single-writer SQLite WAL metadata plus the
same CAS. Count all bytes. Inject crash before/after append, before/after flush, rename/replace,
checkpoint and projection commit; partial/torn/corrupt frame; missing/wrong CAS object; disk full at
each allocation; long reader; slow/dead client; duplicate command; stale writer/reader epoch;
schema/protocol mismatch; migration plus rollback. Recovery either reproduces the exact digest or
returns a typed gap/corrupt/ambiguous refusal. It never truncates or chooses a winner silently.

**Contradiction.** WAL permits one writer at a time but does not identify the authorized writer;
an OS flush does not prove remote media or external effects; atomic replacement depends on the
actual filesystem. JSONL remains a viable simpler candidate.

**Decision.** Adopt the protocol obligations; defer SQLite versus JSONL. Competing option: SQLite
as both store and authority. Failure mode: database serialization is mistaken for an epoch fence.
Falsifier: any stale writer appends successfully, a crash yields two accepted histories, or a slow
view blocks the event writer.

## E-FHAR2-104 — terminal/process broker

**Question.** What cross-platform evidence is required for polished detachable terminals without
giving a terminal authority?

**Direct evidence.** `SRC-V3-021`–`025` and `SRC-V3-063`–`070` establish the bounded mechanics:
ConPTY is UTF-8/VT transport; Windows Jobs have child/breakaway and notification caveats; Linux
process groups are terminal signaling rather than complete containment; cgroup v2 and pidfds add
scope and stable identity; tmux/Zellij/Ratatui/crossterm/xterm.js/MCP Apps expose useful fanout and
render patterns with documented gaps.

**Protocol.** The Recursion broker—not the PTY, renderer or view—owns process identity,
containment, event cursors, input/resize leases, recovery and fanout:

```text
HELLO(epoch, stream, last_cursor, dimensions, capabilities)
WELCOME(replay_floor, snapshot_cursor, leases, capabilities)
SNAPSHOT(...)
EVENT(epoch, cursor, class, process_identity, payload)
ACK(cursor)
CREDIT(bytes, events)
INPUT(command_id, process_epoch, input_lease, bytes)
RESIZE(command_id, process_epoch, resize_lease, columns, rows)
RESET(reason=GAP, snapshot_cursor)
```

Cursor units are UTF-8 bytes for raw data or a distinct event sequence, never host-language string
length. Zero clients does not stop draining. Each view has a bounded credit queue; a slow view is
disconnected with its last cursor. One fenced input lease exists. Attach/detach cannot create a
model turn, process, actor or effect. Output bytes are untrusted data and cannot become broker
commands.

Required tests: `PROC-WIN-01/02` Job-tree and breakaway negatives; `PROC-LNX-01/02` PTY/session,
cgroup and pidfd; `RECON-01` crash/orphan classification; `ATTACH-01`; `CURSOR-01`; `LEASE-01`;
`FLOW-01`; `GOLD-01` for fragmented UTF-8, Unicode width, ANSI/OSC/DCS/control injection,
alternate screen and resize races; `AT-01` for Narrator/NVDA/AT-SPI and plain-text mode; and
`PERF-01` soak with 0/1/5/10/20 views. Pin OS build, kernel, terminal, shell, renderer, Unicode data,
locale, dimensions and assistive technology.

**Contradiction.** Job Objects can admit breakaway/creation-path escapes; cgroup members can migrate
when permissions allow; notification/terminal closure is not proof of descendant or external-effect
completion. UI diffing may reduce flicker without supplying durability or accessibility.

**Decision.** Adopt broker ownership and the matrix; defer renderer and exact cursor store.
Competing option: one PTY/session per visible terminal. Failure mode: view loss kills work or attach
duplicates a model/effect. Falsifier: any silent descendant escape, duplicate effect/model turn,
unbounded slow-client memory, cursor gap without reset or inaccessible authority state.

## E-FHAR2-105 — plugin and frontend isolation

**Question.** What lifecycle makes plugins and rich views optional capabilities rather than
authority or idle cost?

**Direct evidence.** `SRC-V3-004`, `005`, `069`, `070`, `097` and `098` cover update metadata,
provenance, typed negotiation, sandboxed presentation, WebAssembly import/capability isolation and
signature mechanisms. They do not prove a plugin benign. The pinned MCP Apps transport validates
`event.source` but sends with target origin `"*"`; the stronger Recursion adapter must validate exact
source and origin, bind a session nonce and send to an exact target origin.

**Repository-local contract.** Trust tiers are `T0-kernel`, `T1-signed-built-in`,
`T2-signed-isolated-third-party`, `T3-untrusted-view` and `T4-external-engine/provider`.
Lifecycle is `discovered -> verified -> admitted -> staged -> active`; replacement drains and fences
the old epoch before the new one activates; failure enters `quarantined`; revocation enters
`revoked`; removal enters `retired`. Effective capability is the intersection of artifact
declaration, GoalSpec, constitution, route/account, budget, privacy/egress, PAUSE and owner grants;
every deny is preserved. Digest, signature, manifest, license/provenance, protocol/schema, isolation
profile and grant epoch are bound to each activation and receipt.

Disabled means metadata only: no implementation import/compile/instantiate, filesystem discovery
beyond the admitted manifest, process/thread/timer/watcher, network, credential access, quota/cache
write, context injection or tool registration. Test cold/warm boot and activity traces with 0, 10
and 100 installed-but-disabled artifacts. Adversarial fixtures cover digest/signature/substitution,
unknown capability/version, least-privilege intersection, revoked/stale grant, crash/timeout,
reload/drain, state compatibility, malicious WebAssembly imports, browser CSP/origin/source/nonce,
view-generated tool calls, PAUSE and missing provenance/license.

**Contradiction.** A valid signature identifies an artifact/identity under a trust policy; it does
not make behavior safe. WebAssembly sandboxing depends on host imports and runtime correctness.
Any implementation that imports or instantiates installed-but-disabled plugins directly
contradicts the required zero-cost-disabled contract; no registered source is used to claim that
`SRC-V3-097` itself implements such a loader.

**Decision.** Adopt the trust/lifecycle/zero-cost-disabled contract; defer Wasmtime and signing
stack selection. Competing option: trusted in-process plugins. Failure mode: capability mediation
exists on paper while imports or host calls bypass it. Falsifier: disabled code runs or any plugin/
view can alter plan, authority, lease, event or effect status without kernel admission.

## E-FHAR2-106 — canonical context, cache and token accounting

**Question.** How can context and cache optimization be measured without assuming portable caches
or billing controls?

**Direct evidence.** `SRC-V3-034`–`036` and `096` record exact current API controls. OpenAI exposes
implicit/explicit prefix behavior, cache key/breakpoint/TTL and cached/write-token counters on
supported API routes; the key influences routing but does not pin a machine or guarantee a hit.
Anthropic exposes automatic/explicit breakpoints, 5-minute/1-hour TTLs, a 20-block lookback,
workspace/organization isolation differences and read/write counters. Gemini exposes implicit and
explicit cached content, TTL/expiry/delete and cached-token metadata; its official pages contain
conflicting wording about implicit savings, so cost benefit remains unknown until measured.
`SRC-V3-040`, `041`, `054`, `087` and `088` supply pinned compaction/local-cache mechanisms.

**Repository-local contract.** The canonical Context Capsule contains the exact GoalSpec and policy
digests, plan/task/packet identity, authority/privacy/route/budget bindings, relevant source and
artifact digests, event/effect/evidence summaries, unresolved questions, verifier requirements and
compaction derivation. Provider/session/KV caches are disposable accelerators. Cache identity binds
privacy/project/tenant, policy/source/tool/schema/serialization, engine/provider/model/endpoint/
account, template/tokenizer/SDK and compaction version. Counters are `observed`, `estimated`,
`unknown` or `not-applicable`; unavailable is never zero.

Experiment treatments are raw replay, provider-native state, deterministic capsule and hybrid.
Cross cold/warm, same/fresh session and same/cross route where allowed. Change each cache-identity
field separately; measure exact required-field recall, gate quality, drift, cache reads/writes,
ordinary/cached/write/input/output/reasoning tokens, latency, money only from direct receipts and
privacy side-channel isolation. Never send private fixtures to training-eligible routes.

**Contradiction.** API documentation does not establish Codex OAuth/CLI behavior, subscription
debit, hidden counters or cross-provider reuse. An opaque compaction item is not Recursion's
canonical evidence. Cache hits may reduce one metric while write cost, latency or fidelity worsens.

**Decision.** Adopt provider-neutral capsules and exact route descriptors; adapt native caches only
when directly observed. Competing option: standardize on one provider session. Failure mode: route
change loses goal/evidence or cross-tenant prefix identity leaks. Falsifier: capsule treatment fails
required-field fidelity or cannot reproduce the admitted context digest.

## E-FHAR2-107 — evaluation and attribution correction

**Question.** What protocol can attribute improvements to the harness and not task exposure,
attempt pseudoreplication or judge bias?

**Direct evidence.** `SRC-V3-071`–`081` and `099`–`103` support reproducible task environments,
fresh/rotating tasks, contamination limitations, hierarchical uncertainty, judge-bias controls and
current benchmark/harness versioning. Public METR tasks explicitly describe themselves as work in
progress and ask users to limit training exposure. Current mini-SWE-agent is intentionally much
simpler than SWE-agent and is recommended by its maintainers as the default, contradicting the
assumption that a larger scaffold is inherently better. tau2 v1.0.1 states that affected earlier
scores are not comparable after grading fixes. Harbor is a useful versioned runner, not an oracle.

**Defect found.** The prior `PROTO-FHAR-01` counted 48 independent tasks (24 per family) with three
attempts across 12 cells as 1,728 attempts. Attempts on the same task are correlated and do not
create 1,728 independent task units. Therefore the text could not guarantee 80% power for a
5-percentage-point binary-completion improvement. Approximate paired requirements can be near
1,000 or more tasks depending on discordance; no fixed number is adopted without blinded
simulation. The earlier power statement is rejected.

**Replacement protocol `PROTO-FHAR-01-R1`.** Use a sealed Recursion-owned corpus with disjoint
families: F1 planning/replay and F2 terminal/tool/evidence; optional F3 plugin/effect and F4 context/
cache are separate outcome cohorts. Each task binds immutable source/license, creation date,
exposure classification, environment/oracle digest, time/resource/risk profile and deterministic
oracle preflight. The statistical unit is task; attempts/seeds are repeated observations nested
within task.

Run a blinded pilot only to estimate base rate, paired discordance, family variance and missingness.
Before unblinding the main run, publish a simulation/analysis receipt and either expand unique tasks
to the required count or explicitly narrow the minimum detectable effect and label the 48-task set
exploratory. Freeze an H0–H5 cumulative component ladder plus a smaller orthogonal crossed subset so
interactions are estimable. Primary comparisons use fixed total token/time/tool budget,
intention-to-treat missingness and paired/hierarchical intervals. Blind human reviewers to
treatment; calibrate any LLM judge against humans and keep it secondary. Stop only for safety/
privacy breach, oracle invalidity, budget exhaustion or the preregistered precision/futility rule;
no favorable interim peeking.

**Decision.** Adopt R1 and reject the prior power guarantee. Competing option: retain a small fixed
corpus for rapid iteration. Failure mode: benchmark tuning/contamination masquerades as progress.
Falsifier: oracle audit fails, overlap/exposure is material, or a result reverses on fresh held-out
tasks/human review.

## E-FHAR2-108 — release, boot, dependency and migration minimum

**Question.** What smallest release proves the architecture boundary without bundling every future
capability?

**Direct evidence.** `SRC-V3-004`, `005`, `097`, `098`, `105` and `106` distinguish update
integrity, provenance, signatures, reproducible artifacts, versioning and SBOMs. None proves semantic
safety. `SRC-V3-052`–`062` show that external harnesses and durable runtimes provide mechanisms but
not Recursion authority. SemVer describes public-API compatibility; it is insufficient for schema,
constitution and artifact compatibility.

**Repository-local release contract.** `ReleaseId` contains:

```text
product_semver
protocol_major + protocol_minor
schema_epoch
constitution_policy_digest
core_artifact_digest
core_dependency_lock_digest
build_provenance_digest
sbom_digest
edition_manifest_digest
```

`BootReceipt` binds that identity, manifest/lock/core digests, state/checkpoint digest, event
high-water, recovery disposition and each optional capability as `absent`, `disabled`,
`incompatible`, `unverified`, `quarantined` or `active`. Core must verify release metadata, replay
checkpoint/events, verify sequence/digests, reconcile leases/effects/PAUSE and expose owner
status/replay with every provider, engine, plugin and frontend absent. Missing optional capability
blocks only dependent mutation; it never auto-installs, substitutes a route, spends or becomes a
pass. SPDX 3.0.1 is the proposed canonical SBOM; CycloneDX may be a derived export.

Hermes migration is aggregate scoped: freeze legacy state; compatibility read; produce import
digest; shadow compare; establish exactly one writer; advance/fence epoch; cut over; retain legacy
read-only projection; allow verified rollback only before an external effect. After a real or
ambiguous effect, reconcile forward. Remove the adapter only after an owner-defined clean window,
no Hermes-specific canonical events/writes, passing import/replay/recovery/rollback fixtures and a
migration guide. Copied code requires file-level provenance and license notices; public visibility
or clean-room intent is not automatic legal clearance.

Track, but do not invent ceilings for, privileged/total LOC, direct/transitive dependencies and
depth, binary/install size, imports, cold/warm CPU/RSS/handles/threads/syscalls, IPC endpoints,
schema/events/verbs, code owners, vulnerability/license surface, churn and replay/test duration.
Every new kernel dependency needs a Feature Admission Contract, adapter-alternative analysis,
disabled-path trace and removal plan.

**Contradiction.** The existing edition text required one provider/engine in `core`; that violates
adapter-free boot and is superseded in the v3 design. “Zero dependencies” would also be misleading:
ordinary pinned libraries are allowed, but none may own or reconstruct canonical Recursion state.

**Decision.** Adopt the release/boot contract; adapt packaging after measurement. Competing option:
five fixed editions or a provider-bundled core. Failure mode: optional code becomes a boot/recovery
dependency or SemVer masks a policy/schema mismatch. Falsifier: core cannot replay and report safely
with all optional artifacts uninstalled.

## Cross-lane synthesis

The ratified architecture is a **small semantic kernel**, not a mandate to rewrite every optimized
loop. The strongest source-grounded findings are:

1. Canonical identity, GoalSpec/plan state, event/effect truth, leases/fences, PAUSE and verification
   must be recoverable from the versioned Recursion release without an external harness.
2. Every optimization surface—provider loop, cache, database, process broker, plugin or view—has a
   typed capability boundary and is replaceable without changing logical actor identity.
3. Durability, signatures, sandboxing, containerization, formal checking and same-family review
   each cover different failure classes; none is a synonym for authority, safety or correctness.
4. The path to a frontier claim is a sealed, statistically valid comparative program. The current
   work establishes architecture and experiments only.

The strongest contradiction is that mature minimal harnesses can remain competitive while larger
systems accumulate dependencies and lifecycle coupling. Therefore Recursion earns complexity only
one measured capability at a time. Any native provider loop, database choice, plugin runtime,
terminal renderer or cache strategy remains conditional until its preregistered comparison passes
all hard floors and has a removal path.
